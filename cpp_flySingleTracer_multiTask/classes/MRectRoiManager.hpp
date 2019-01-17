#ifndef _MRECTROIMANAGER_HPP_
#define _MRECTROIMANAGER_HPP_

#include "MMacros.h"
#include "MRectRoi.hpp"
#include "MDataManager.hpp"
#include "MPredictor.hpp"
using namespace cv;
using namespace std;

class MRectRoiManager {
private: // members
	Vector<MRectRoi*> _VRoi; // roi array
	RNG* _pRng; //color generator
	Mat _imgConfig; //label image of roi

public: // constructor
	MRectRoiManager() {
		//generate rng
		_pRng = new RNG(12345);
	}

public: // I/O communication
	
	bool importConfig(MDataManager* pManData) { // load roi data
		// stop writing configuration
		int isExist = _access(pManData->data_fConfig.c_str(), 0);
		if (isExist == -1) {
			cout << "No previous configuration file found.\n";
			pManData->resetConfigFile();
			return false;
		}
		FileStorage *pConfig = new FileStorage(pManData->data_fConfig, FileStorage::READ);
		if (!pConfig->isOpened()) {
			cout << "[warning: configure] File not found.\n";
			return false;
		}

		//get roi number'
		int countBox = -1;
		(*pConfig)["count_box"] >> countBox;
		if (countBox < 1){
			cout << "[warning: configure] No saved roi configurations.\n";
			return false;
		}

		//get roi data
		vector<int> rc;
		MRectRoi *mrr = NULL;
		for (int i = 0; i<countBox; i++)
		{
			char word[64]; sprintf_s(word, "roi_%d", i);
			(*pConfig)[word] >> rc;
			mrr = new MRectRoi(rc[0], rc[1], rc[2], rc[3]);
			this->append(mrr);
		}
		pConfig->release();
		return true;
	}

	// save roi data
	void exportConfig(MDataManager* pManData) {
		// get file pointer
		FileStorage* pConfig = new FileStorage(pManData->data_fConfig, FileStorage::APPEND);
		// export box number 
		int countBox = (int)_VRoi.size();
		(*pConfig) << "count_box" << countBox;
		// write each roi
		for (int i = 0; i<countBox; i++) {
			char word[64]; sprintf_s(word, "roi_%d", i);
			(*pConfig) << word << _VRoi[i]->getRect();
		} pConfig->release();

		// export label image
		string dst = pManData->data_rootPath + "order.png";
		if(!toolpath::isFileExist(dst))
			imwrite(dst, _imgConfig);
	}
	
public: // get components
	// get roi number
	int getSize() {
		return (int)_VRoi.size();
	}

	// get an roi pointer
	MRectRoi* getRoi(int i) {
		return _VRoi[i];
	}

	MRectRoi* getLastRoi() {
		if (getSize() == 0) return NULL;
		else return _VRoi[_VRoi.size() - 1];
	}
	
	// get all roi
	vector<Rect> getAllRois() {
		vector<Rect> VRc;
		for (int i = 0; i < (int)_VRoi.size(); i++) {
			VRc.push_back(_VRoi[i]->getRect());
		}
		return VRc;
	}

public:
	void initRoiSeriesWith(Mat& imgFr) {
		string wConfig = "set roi series";
		namedWindow(wConfig, CV_WINDOW_NORMAL);
		//prepare the canvas for setting rois
		Mat imgConfig = imgFr.clone();
		// print hint
		putText(imgConfig, "[Space]=Confirm, [Esc]=End",
			Point(10, 25), CV_FONT_HERSHEY_SIMPLEX, 1, Scalar(0, 255, 0));
		int cBoxes = 0;
		Point ptNum;
		char szNum[64];
		if ((int)_VRoi.size() > 0) { // already load previous rois
			for (int i = 0; i < (int)_VRoi.size(); i++) { // paint all previous rois
				// draw this roi on next scene
				sprintf(szNum, "%d", cBoxes);
				ptNum.x = _VRoi[i]->getRect().x;
				ptNum.y = _VRoi[i]->getRect().y;
				putText(imgConfig, szNum, ptNum, CV_FONT_HERSHEY_SIMPLEX, 1, _VRoi[i]->color);
				rectangle(imgConfig, _VRoi[i]->getRect(), _VRoi[i]->color, 2);
				cBoxes++;
			}
		}
		// set-roi loop
		MRectRoi* roi = NULL;
		int key = -1;
		while (1) {
			// draw a new window
			roi = new MRectRoi();
			key = roi->setRoi(wConfig.c_str(), imgConfig);
			if (roi->getRect().width * roi->getRect().height != 0) { // only save valid roi
				// save this roi
				this->append(roi);
				// draw this roi on next scene
				sprintf(szNum, "%d", cBoxes);
				ptNum.x = roi->getRect().x;
				ptNum.y = roi->getRect().y;
				putText(imgConfig, szNum, ptNum, CV_FONT_HERSHEY_SIMPLEX, 1, roi->color);
				rectangle(imgConfig, roi->getRect(), roi->color, 2);
			} cBoxes++;
			// tell if end setting roi or not
			if (key == 27) {
				cout << _VRoi.size() << " roi established.\n";
				break;
			}
		} _imgConfig = imgConfig.clone(); // save label image
		destroyWindow(wConfig);
	}

	void initAutoRoiSeriesWith(Mat& imgFr) {
		string wConfig = "batch setting of roi";
		//namedWindow(wConfig, CV_WINDOW_NORMAL);
		//prepare the canvas for setting rois
		Mat imgConfig = imgFr.clone();
		Mat imgGrayConfig; cvtColor(imgConfig, imgGrayConfig, CV_BGR2GRAY);
		// print hint
		putText(imgConfig, "[Space]=Confirm, [Esc]=End",
			Point(10, 25), CV_FONT_HERSHEY_SIMPLEX, 1, Scalar(0, 255, 0));
		int cBoxes = 0;
		Point ptNum;
		char szNum[64];
		MPredictor* mp = new MPredictor;
		if (mp->loadModel(
			mod_predict_mu, 
			mod_predict_sigma, 
			mod_predict_Theta1, 
			mod_predict_Theta2
			)) { // batch locating tubes
			vector<Rect> lTempRois = mp->predictMultipleLine(imgGrayConfig);
			for (size_t i = 0; i < lTempRois.size(); i++) {
				this->append(lTempRois[i]);
			}
			for (int i = 0; i < (int)_VRoi.size(); i++) { // paint all rois
				// draw this roi on next scene
				sprintf(szNum, "%d", cBoxes);
				ptNum.x = _VRoi[i]->getRect().x;
				ptNum.y = _VRoi[i]->getRect().y;
				putText(imgConfig, szNum, ptNum, CV_FONT_HERSHEY_SIMPLEX, 1, _VRoi[i]->color);
				rectangle(imgConfig, _VRoi[i]->getRect(), _VRoi[i]->color, 2);
				cBoxes++;
			}
		}
		// report and adjustment of rois
		MRectRoi* roi = NULL;
		int key = -1;
		while (1) {
			// draw a new window
			roi = new MRectRoi();
			key = roi->setRoi(wConfig.c_str(), imgConfig);
			if (roi->getRect().width * roi->getRect().height != 0) { // only save valid roi
				// save this roi
				this->append(roi);
				// draw this roi on next scene
				sprintf(szNum, "%d", cBoxes);
				ptNum.x = roi->getRect().x;
				ptNum.y = roi->getRect().y;
				putText(imgConfig, szNum, ptNum, CV_FONT_HERSHEY_SIMPLEX, 1, roi->color);
				rectangle(imgConfig, roi->getRect(), roi->color, 2);
			} cBoxes++;
			// tell if end setting roi or not
			if (key == 27) {
				cout << _VRoi.size() << " roi established.\n";
				break;
			}
		} _imgConfig = imgConfig.clone(); // save label image
		
		destroyWindow(wConfig);
	}

private: //internal op
	//add
	void append(Rect& rc) {
		//create new roi
		MRectRoi* pRoi = new MRectRoi(rc.x, rc.y, rc.width, rc.height);
		_VRoi.push_back(pRoi);

		//set labeling properties
		pRoi->color = Scalar(_pRng->uniform(0, 255), _pRng->uniform(0, 255), _pRng->uniform(0, 255));
	}

	void append(int x, int y, int w, int h) {
		//create new roi
		MRectRoi* pRoi = new MRectRoi(x, y, w, h);
		_VRoi.push_back(pRoi);

		//set labeling properties
		pRoi->color = Scalar(_pRng->uniform(0, 255), _pRng->uniform(0, 255), _pRng->uniform(0, 255));
	}

	void append(MRectRoi* pRoi) {
		_VRoi.push_back(pRoi);

		//set labeling properties
		pRoi->color = Scalar(_pRng->uniform(0, 255), _pRng->uniform(0, 255), _pRng->uniform(0, 255));
	}

	//delete
	void remove(int iRm) {
		MRectRoi* eToRm = _VRoi[iRm];
		for(int i=iRm;i<(int)_VRoi.size()-1;i++) {
			_VRoi[i] = _VRoi[i+1];
		} _VRoi.pop_back();
		delete eToRm;
	}

	//clear all roi
	void clearAll() {
		_VRoi.clear();
	}

};

#endif