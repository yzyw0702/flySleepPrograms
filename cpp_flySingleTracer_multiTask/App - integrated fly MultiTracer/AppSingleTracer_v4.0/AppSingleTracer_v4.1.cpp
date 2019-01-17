// AppSingleTracer_v4.0.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include "../../classes/MMacros.h"
#include "../../classes/MVideoManager.hpp"
#include "../../classes/MDynamicGrBgManager.hpp"
#include "../../classes/MPredictor.hpp"
#include "../../classes/MTracerManager.hpp"
#include "../../classes/MDataManager.hpp"
#include "../../classes/MPathTool.hpp"
#include "../../classes/MStringTool.hpp"
#include "../../classes/MSingleTask.hpp"
#include <ppl.h>
using namespace std;
using namespace cv;
using namespace Concurrency;

vector<Rect> semiautodetect(Mat& imgBgGr) {
	MPredictor *pPred = new MPredictor();
	pPred->loadModel("Mu.txt", "Sigma.txt", "Theta1.txt", "Theta2.txt");
	return pPred->predictMultipleLine(imgBgGr);
}

/*	# process tracing task for one directory
	rootpath = full path name of task directory;
	ret = -1 means no video clips;
*/
int configSingleTask(string rootpath) {
	// # get clips list
	if (rootpath.size() == 0) rootpath = "./";
	string pathAvi = toolpath::joinPath(rootpath, "*.avi");
	vector<string> lClips = toolpath::getFiles(pathAvi);
	if (lClips.size() == 0) {  // warning: no clips found
		cout << "No video clips in " << rootpath << endl;
		return -1;
	}

	// # output clip list in rootpath
	string pathLsAvi = toolpath::joinPath(rootpath, "list.txt");
	ofstream hLsAvi(pathLsAvi);
	for (int i = 0; i < (int)lClips.size(); i++){
		hLsAvi << lClips[i] << endl;
	} hLsAvi.close();

	// # init data manager
	MDataManager *pData = new MDataManager;
	pData->initRootPath(rootpath.c_str());
	pData->initIOFiles();
	pData->resetIOFileStream();

	// # init a video group
	MVideoManager* pVid = new MVideoManager(rootpath.c_str(), 1);
	//pVid->writeData(pData);
	pVid->exportConfig(pData);

	// # init dynamic background
	MDynamicGrBgManager* pBg = new MDynamicGrBgManager();
	pBg->initWith(pVid);
	pBg->exportConfig(pData);

	// # init Rect roi
	MRectRoiManager* pRoi = new MRectRoiManager();
	Mat imgFrTmp; pVid->readPerCall(imgFrTmp);
	pVid->resetTimer();
	if (!pRoi->importConfig(pData))
		pRoi->initAutoRoiSeriesWith(imgFrTmp);
	pRoi->exportConfig(pData);

	// # init light monitor
	MLightMonitor* pLight = new MLightMonitor();
	pLight->importConfig(pData);
	pLight->setReference(imgFrTmp);
	pLight->exportConfig(pData);

	// # init length ratio
	MTracerManager* pTracers = new MTracerManager();
	pTracers->importConfig(pData);
	pTracers->setTracerWith(pRoi, imgFrTmp, pBg->getBg());
	pTracers->exportConfig(pData);
	
	// export configuration data
	pBg->clear();
	pData->closeIOFiles();
    return 0;
}

int traceSingleTask(string rootpath, bool isShowGraph = true) {
	// # init tracing task
	MSingleTask* pTask = new MSingleTask;
	cout << "How many frames to trace per second? cps = ";
	int cps = 1; cin >> cps;
	cout << "Start tracing at (-1 or 0 means start from the 1st clip) #Clip = ";
	int iStartClip = -1; cin >> iStartClip;
	cout << "Start tracing at (-1 or 0 means start from the 1st frame) #Fr = ";
	int iStartFr = -1; cin >> iStartFr;
	cout << "Stop tracing at (-1 means stop at the last clip) #Clip = ";
	int iStopClip = -1; cin >> iStopClip;
	cout << "Stop tracing at (-1 means stop at the last fr) #Fr = ";
	int iStopFr = -1; cin >> iStopFr;
	pTask->initWith(rootpath, cps, false, iStartClip, iStartFr, iStopClip, iStopFr);
	
	// # video loop
	namedWindow(wTest, CV_WINDOW_NORMAL);
	Mat imgLabel;
	while (1) {
		if (pTask->computeNextFrame()) {
			if (isShowGraph) {
				pTask->labelWith(imgLabel);
				imshow(wTest, imgLabel);
			}
			pTask->reportProgress();
			pTask->writeData();
		}
		else {
			break;
		}
		if (isShowGraph) {
			int key = waitKey(1);
			if (key == 27) {
				pTask->stop();
			}
		}
	}
	pTask->release();
	destroyWindow(wTest);

	return 0;
}

int configMultiTask(string workdir, string fTasklist) {
	string pathTasklist = toolpath::joinPath(workdir, fTasklist);
	ifstream hTasklist(pathTasklist);
	string line;
	while (getline(hTasklist, line)) {
		cout << "\tConfigure #task [" << line << "]\n";
		configSingleTask(line);
	}
	hTasklist.close();
	return 0;
}

int traceMultiTask(string workdir, string fTasklist, bool isShowGraph = false) {
	// # init multi tracing tasks
	vector<MSingleTask*> lpTasks;
	// cout << "How many frames to trace per second? cps = ";
	int cps = 1;
	// cin >> cps;
	int iStartClip = -1;
	int iStartFr = -1;
	int iStopClip = -1;
	int iStopFr = -1;
	// cout << "Do you want to define the times to start/stop tracing?\n\t0 = no;\n\t1 = yes\n\tYour choice = ";
	int isDefineTime = 0;
	// cin >> isDefineTime;
	if (isDefineTime) {
		cout << "Start tracing at (-1 or 0 means start from the 1st clip) #Clip = ";
		cin >> iStartClip;
		cout << "Start tracing at (-1 or 0 means start from the 1st frame) #Fr = ";
		cin >> iStartFr;
		cout << "Stop tracing at (-1 means stop at the last clip) #Clip = ";
		cin >> iStopClip;
		cout << "Stop tracing at (-1 means stop at the last fr) #Fr = ";
		cin >> iStopFr;
	}
	//cout << "Dow you want to refine ROI settings? (0=no / 1=yes) Your Choice = ";
	int isRefineRoi = 0;
	//cin >> isRefineRoi;

	ifstream hTasklist(toolpath::joinPath(workdir, fTasklist));
	string line;
	MSingleTask* pTmp = NULL;
	vector<string> lsPaths;
	while (getline(hTasklist, line)) {
		cout << "Task #" << line << endl;
		lsPaths.push_back(line);
		pTmp = new MSingleTask;
		pTmp->initWith(line, cps, false, iStartClip, iStartFr, iStopClip, iStopFr, isRefineRoi);
		lpTasks.push_back(pTmp);
	}
	hTasklist.close();

	// # multi video loop in parallel
	/* process while labeling */
	int nTasks = (int)lpTasks.size();
	Mat* lsImgLabel = new Mat[nTasks];
	if (isShowGraph) {
		for (int i = 0; i < nTasks; i++) {
			namedWindow(lsPaths[i], CV_WINDOW_NORMAL);
		}
	}

	/* multi tracing loop */
	int key = 1;
	int nStop = 0;
	while (1) {
		parallel_for(0, (int)lpTasks.size(), [&](int i) {
			//for (int i = 0; i < nTasks; i++) {
			if (lpTasks[i]->computeNextFrame()) {
				if (isShowGraph) {
					lpTasks[i]->labelWith(lsImgLabel[i]);
				}
				lpTasks[i]->writeData();
			}
			else {
				lpTasks[i]->stop();
			}
		});

		for (int i = 0; i < nTasks; i++) {
			if (isShowGraph) {
				imshow(lsPaths[i], lsImgLabel[i]);
			}
			else {
				lpTasks[i]->reportProgress();
			}
		}
		if (isShowGraph) {
			key = waitKey(1);
		}
		nStop = 0;
		for (int i = 0; i < nTasks; i++) {
			if (lpTasks[i]->isStop()) {
				nStop++;
			}
		}
		if (nStop == nTasks) {
			key = 27;
		}
		if (key == 27) {
			for (int i = 0; i < nTasks; i++) {
				lpTasks[i]->stop();
				if (lpTasks[i]->isStop()) {
					cout << "Task #" << i << " has stop." << endl;
				}
			} break;
		}
	}
	for (int i = 0; i < nTasks; i++) {
		lpTasks[i]->release();
		if (isShowGraph) {
			destroyAllWindows();
		}
	}
	return 0;
}


int main(int argc, char** argv) {
	string rootpath = "";
	string mode = "configure";
	if (argc > 2) {
		for (int i = 1; i < argc; i++)
			if (i == 1) {
				mode = argv[1];
				cout << "\tmode switched to " << mode << endl;
			}
			else if (i == 2)
				rootpath = argv[i];
			else if (i > 2){
				rootpath += " ";
				rootpath += argv[i];
			}
	}
		
	else {
		cout << "task working directory: ";
		char bufRootpath[2048];
		cin.getline(bufRootpath,2048);
		rootpath = bufRootpath;
		cout << "configure or tracing?\n\t0=configure;\n\t1=tracing\n\tYour Choice = ";
		int iChoice = 0; cin >> iChoice;
		if (iChoice = 0) mode = "configure";
		else mode = "tracing";
	}
	int ret = -1;
	if (mode == "configure") {
		cout << "\tConfigure tracing program:\n";
		ret = configMultiTask(rootpath, "tasklist.txt");
	}
	else if (mode == "tracing") {
		//cout << "Show tracing videos?\n\t0 = no;\n\t1 = yes\n\tYour choice = ";
		int isPreview = 0;
		//cin >> isPreview;
		ret = traceMultiTask(rootpath, "tasklist.txt", isPreview);
	}
	
	return ret;
}
