#include "MMacros.h"
#include "MVideoManager.hpp"
#include "MDataManager.hpp"
#include "MRectRoiManager.hpp"
#include "MLightMonitor.hpp"
#include "MDynamicGrBgManager.hpp"
#include "MTracerManager.hpp"
#include "MSingleTask.hpp"
#include "MReplay.hpp"
using namespace std;
using namespace cv;

void testTracing(){
	/* input parameters */
	string rootPath = "D:\\video\\20150714_FLIC-test\\raw\\";
	//string rootPath = ".\\";
	string fClips = "list.txt";
	string fConfig = "config.yaml";
	string pathClips = rootPath + fClips;

	/* init data manager */
	MDataManager* pData = new MDataManager;
	pData->initRootPath(rootPath.c_str());
	pData->initIOFiles();

	/* init and input video clips */
	MVideoManager* pClips = new MVideoManager(rootPath.c_str());
	pClips->initFromDeNovo();

	/* init Roi manager */
	MRectRoiManager* pRois = new MRectRoiManager;
	Mat imgFr; pClips->readPerCall(imgFr);
	pRois->importConfig(pData);
	pRois->initRoiSeriesWith(imgFr);

	/* init light monitor */
	MLightMonitor* pLit = new MLightMonitor;
	pLit->importConfig(pData);
	pLit->setReference(imgFr);

	/* init background */
	pClips->resetTimer();
	MDynamicGrBgManager* pBg = new MDynamicGrBgManager;
	pBg->initByGpuWith(pClips);
	//pBg->initWith(pClips);

	/* init tracers */
	MTracerManager* pTracers = new MTracerManager;
	pTracers->importConfig(pData);
	pTracers->setTracerWith(pRois, imgFr, pBg->clone());

	/* export roi config */
	pData->resetConfigFile(); // previous configuration data all swapt from here
	pRois->exportConfig(pData);

	/* export bg config */
	pBg->exportConfig(pData);

	/* export light monitor config */
	pLit->exportConfig(pData);

	/* export tracer config */
	pTracers->exportConfig(pData);

	/* ask how many frames should be traced */
	cout << "How many frames to process per second? your answer = ";
	int cps = 1; cin >> cps;
	pClips->setCps(cps);

	/* video tracing loop */
	namedWindow(wTest, CV_WINDOW_NORMAL);
	pClips->resetTimer();
	Mat imgBuff, imgLabel;
	int iClip=0, iFr=0;
	while (pClips->readPerCall(imgBuff)) {
		imgFr = imgBuff.clone(); // clone from frame buffer
		//pTracers->detect(imgFr, pBg->getBg()); // detect targets, compute location & speed
		//pBg->renew(imgFr);
		if (imgFr.rows*imgFr.cols == 0) { // jump if current frame is empty
			cout << "[warning] Current frame is missing." << endl;
			continue;
		}
		pTracers->detectByGpu(imgFr, pBg->getGBg()); // detect targets, compute location & speed
		pBg->renewByGpu(imgFr); // renew background
		pLit->computeIByGpu(pTracers->getGFrGr());

		pClips->writeData(pData); // write indices of frame played
		pTracers->writeData(pData); // write location & speed
		pLit->writeData(pData); // write light intensity data

		pClips->getTime(iClip, iFr); // get time point
		if (iFr % 1000 == 0) {
			cout << "Clip #" << iClip << ", Fr #" << iFr << endl;
		}

		imgLabel = imgFr.clone();
		pTracers->labelOn(imgLabel, iClip, iFr); // label trace
		imshow(wTest, imgLabel); // report trace detection
		int key = waitKey(1); // check keyboard event
		if (key == 27) break; // exit by pressing Esc

		//if (iClip >= 1) break;
	}

	/* export video config */
	pClips->exportConfig(pData);

	/* close and clean */
	pLit->exportSummary(pData);
	pData->exportSummary();
	pData->closeIOFiles();
}

void singleTask() {
	/* input parameters */
	//string rootPath = "D:\\video\\20150714_FLIC-test\\raw\\";
	string rootPath = ".\\";
	/* establish a new task */
	MSingleTask* pTask = new MSingleTask;
	pTask->initWith(rootPath,5);
	/* process while labeling */
	namedWindow(wTest, CV_WINDOW_NORMAL);
	Mat imgLabel;
	while (1) {
		if (pTask->computeNextFrameByGpu()) {
			pTask->labelWith(imgLabel);
			imshow(wTest, imgLabel);
			pTask->reportProgress();
			pTask->writeData();
		}
		else {
			break;
		}
		int key = waitKey(1);
		if (key == 27) {
			pTask->stop();
		}
	}
	pTask->release();
	destroyWindow(wTest);
}

void configureSingleTask() {
	/* input parameters */
	//string rootPath = "D:/video/20150503_UR_elav-appl-cs_sleep_sd/raw/d1ch1/";
	string rootPath = ".\\";
	/* establish a new task */
	MSingleTask* pTask = new MSingleTask;
	pTask->initWith(rootPath, 5);
}

void queueTask() {
	/* input list of Tasks */
	const int cTasks = 3;
	string lsPaths[cTasks] = {
		"D:\\video\\20150714_FLIC-test\\raw\\",
		"D:\\video\\20150702_isoCS-sleep\\ch7\\",
		"D:\\video\\20150702_isoCS-sleep\\ch9\\"
	};
	/* init tasks */
	vector<MSingleTask*> VPTasks;
	MSingleTask *pTask = NULL;
	for (int i = 0; i < cTasks; i++) {
		pTask = new MSingleTask;
		cout << "Task #" << i << ":" << endl
			<< "rootpath = " << lsPaths[i] << endl
			<< "the cps of this task = ";
		int cps=1; cin >> cps;
		pTask->initByGpuWith(lsPaths[i],cps);
		VPTasks.push_back(pTask);
	}
	/* process while labeling */
	Mat lsImgLabel[cTasks];
	for (int i = 0; i < cTasks; i++) {
		namedWindow(lsPaths[i], CV_WINDOW_NORMAL);
	}
	int key = 1;
	int cStop = 0;
	while (1) {
		parallel_for(0, (int)VPTasks.size(), [&](int i){
		//for (int i = 0; i < cTasks; i++) {
			if (VPTasks[i]->computeNextFrameByGpu()){
				VPTasks[i]->labelWith(lsImgLabel[i]);
				VPTasks[i]->writeData();
			} else {
				VPTasks[i]->stop();
			}
		//}
		});

		for (int i = 0; i < cTasks; i++) {
			imshow(lsPaths[i], lsImgLabel[i]);
			VPTasks[i]->reportProgress();
		}

		key = waitKey(1);
		cStop = 0;
		for (int i = 0; i < cTasks; i++) {
			if (VPTasks[i]->isStop()) {
				cStop++;
			}
		}
		if (cStop == cTasks) {
			key = 27;
		}
		if (key == 27) {
			for (int i = 0; i < cTasks; i++) {
				VPTasks[i]->stop();
				if (VPTasks[i]->isStop()) {
					cout << "Task #" << i << " has stop." << endl;
				}
			} break;
		}
	}
	for (int i = 0; i < cTasks; i++) {
		VPTasks[i]->release();
		destroyWindow(lsPaths[i]);
	}
}

void replay() {
	/* input parameter */
	//string rootPath = ".\\";
	string rootPath = "D:\\video\\20150718_starve-death-curve_isoCS\\first_batch\\002\\";
	/* init replayer */
	MReplay* pReplay = new MReplay(rootPath.c_str());
	/* replay loop */
	int key = 0;
	pReplay->resetTimer();
	cout << "replay from N Second. N = ";
	int iFrReplay = 0; cin >> iFrReplay;
	pReplay->startFrom(iFrReplay);
	cout << "replay speed = S (frame per second): ";
	int replay_fps = 10; cin >> replay_fps;
	namedWindow(wTest, CV_WINDOW_NORMAL);
	while (pReplay->showNextFrame(string(wTest))) {
		key = waitKey(1000 / replay_fps);
		if (key == 27) break;
	} pReplay->stop();
	destroyWindow(wTest);
}

void exportReplayWith(string& rootPath, int start, int stop) {
	/* init replayer */
	MReplay* pReplay = new MReplay(rootPath.c_str());
	/* init output directory */
	string pathOut = rootPath + "replay";
	string cmdCreatePath = "mkdir " + pathOut;
	system(cmdCreatePath.c_str());
	pathOut += "\\";
	/* replay loop */
	pReplay->resetTimer();
	pReplay->startFrom(start);
	char szWord[128];
	int idx = start;
	while (1) {
		sprintf(szWord, "%sfr_%d.jpeg", pathOut.c_str(), idx++);
		if (!pReplay->exportNextFrame(szWord)) break;
		if (idx == stop) break;
	} pReplay->stop();
	printf("[%s]: from %d sec to %d sec has been exported.\n", rootPath.c_str(), start, stop);
	delete pReplay;
}

void exportReplayQueue() {
	struct RTask {
		string task;
		int start;
		int stop;
		RTask() {
			task = ".\\";
			start = 0;
			stop = 0;
		}
		RTask(stringstream& ssInput) {
			ssInput >> task;
			ssInput >> start;
			ssInput >> stop;
			if (task[task.size() - 1] != '\\') {
				task += "\\";
			}
		}
	};
	/* get input task list */
	cout << "replay task list: ";
	string fTaskList; cin >> fTaskList;
	ifstream hLTasks(fTaskList, ios::in);
	if (!hLTasks.is_open()) return;
	/* parse task list */
	vector<RTask> VTasks;
	stringstream ssTask;
	string sInput;
	while (getline(hLTasks, sInput)) {
		ssTask = stringstream(sInput);
		VTasks.push_back(RTask(ssTask));
	}
	/* set replay speed */
	/* replay task by task */
	for (size_t i = 0; i < VTasks.size(); i++) {
		exportReplayWith(VTasks[i].task, VTasks[i].start, VTasks[i].stop);
	}

}

void testIStream() {
	string s = "This\tis\ta\ttest\tfor\tsplitting.\n";
	stringstream ss(s);
	string w; int c = 0;
	while (ss >> w) {
		cout << w << endl;
		c++;
	} cout << "count = " << c << endl;
}

void testVectorCopy() {
	Vector<int> a;
	Vector<int> ca;
	a.push_back(10);
	a.push_back(12);
	a.push_back(14);
	a.push_back(16);
	ca = a;

	a.clear();

	cout << "a: ";
	for (int i = 0; i < (int)a.size(); i++) {
		cout << a[i] << ", ";
	} cout << endl;
	cout << "ca: ";
	for (int i = 0; i < (int)ca.size(); i++) {
		cout << ca[i] << ", ";
	} cout << endl;

}

void seekLine(ifstream* pF, int iL) { // seek position before target line
	string buff;
	for (int i = 0; i < iL; i++) {
		getline(*pF, buff);
	}
}

void testFileSeek() {
	string path = "D:\\video\\20150702_isoCS-sleep\\ch7\\vid_time.txt";
	ifstream *pIfs = new ifstream(path, ios::in);
	seekLine(pIfs, 1);
	string line; getline(*pIfs, line);
	cout << line;
	pIfs->close();
}
