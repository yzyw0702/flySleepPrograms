
//===========================
//====>  MLightMonitor
//===========================
#include "MMacros.h"
#include "MRectRoi.hpp"
#include "MDataManager.hpp"
using namespace std;
using namespace cv;

#ifndef _MLIGHTMONITOR_HPP_
#define _MLIGHTMONITOR_HPP_

class MLightMonitor {
private: // members
	Mat _imgRef;
	gpu::GpuMat _gRef;
	Rect _roiRef; // reference image to monitor light
	float _intensity; // image intensity
	float _maxI; // max intensity imgRef could reach

public: // interfaces
	/* constructor */
	MLightMonitor() {
		_roiRef = Rect(-1, -1, 0, 0);
	}

public:
	// interactive settings of reference roi
	void setReference(Mat& imgFr) {
		// make a copy of reference
		Mat cpyFr = imgFr.clone();
		// set roi
		if (_roiRef.width * _roiRef.height <= 0) {
			MRectRoi *pRr = new MRectRoi;
			namedWindow("setLightMonitorRoi");
			pRr->setRoi("setLightMonitorRoi", cpyFr);
			destroyWindow("setLightMonitorRoi");
			_roiRef = pRr->getRect();
		}
		_maxI = (float)(_roiRef.width * _roiRef.height * 255);
	}

	// show reference image
	void showReference(const char* wPreview, Mat& imgFr) {
		imshow(wPreview,imgFr(_roiRef));
	}

	// compute light intensity
	// ## input: CV_8UC1 img
	float computeI(Mat& imgGr) {
		// compute current intensity
		_imgRef = imgGr(_roiRef);
		_intensity = (float)sum(_imgRef)[0] / _maxI;
		return _intensity;
	}
	float computeIByGpu(gpu::GpuMat& gGr) {
		// compute current intensity
		_gRef = gGr(_roiRef);
		_intensity = (float)gpu::sum(_gRef)[0] / _maxI;
		return _intensity;
	}

public: // I/O with data manager

	// write stream
	void writeData(MDataManager* pManData) {
		char data[64];
		sprintf(data,"%f\n",_intensity);
		(*pManData->light_pIofsIt) << data;
	}

	// import configuration to data manager
	void importConfig(MDataManager* pManData) {
		FileStorage* pFsConfig = new FileStorage(pManData->data_fConfig, FileStorage::READ);
		if (!pFsConfig->isOpened()) { // avoid invalid storage
			cout << "Import light_config failed!\n";
			return;
		}
		vector<int> rc;
		(*pFsConfig)["light_roiRef"] >> rc;
		if (rc.size() == 4) {
			_roiRef = Rect(rc[0], rc[1], rc[2], rc[3]);
		}
		pFsConfig->release();
	}

	// export configuration to data manager
	void exportConfig(MDataManager* pManData) {
		FileStorage* pFsConfig = new FileStorage(pManData->data_fConfig, FileStorage::APPEND);
		if(!pFsConfig->isOpened()) { // avoid invalid storage
			cout << "Export light_config failed!\n";
			return;
		}
		(*pFsConfig) << "light_roiRef" << _roiRef;
		pFsConfig->release();
	}

	// export summary data: read light data and classify into 0(dark) or 1(bright)
	// ## warning: use after tracing 
	void exportSummary(MDataManager* pManData) {
		// start reading data file from the very beginning
		pManData->resetIOFileStream();

		// read light data
		fstream *pfs = pManData->light_pIofsIt;
		
		// discard header
		string sVal;
		*pfs >> sVal;
		// compute threshold (=avergage) of intensity data
		float avg = 0.0; // average of intensity
		float cVal = 0.0; // number of values
		vector<float> VIt(1000);
		while(*pfs >> sVal) {
			float it = (float)atof(sVal.c_str());
			avg += it;
			VIt.push_back(it);
			cVal += 1.0;
		} avg /= cVal;
		// check light switch points
		int curr = 0;
		int prev = -1;
		vector<int> timeSwitch;
		vector<int> statii;
		for (int t = 0; t < (int)VIt.size(); t++) {
			if (VIt[t] < avg) { // dark
				curr = 0;
			} else { // light
				curr = 1;
			}
			if (curr != prev) {
				timeSwitch.push_back(t); // 0-based time points
				statii.push_back(curr); // 0=dark; 1=light
			}
			// update prev
			prev = curr;
		}
		// add the last section
		timeSwitch.push_back((int)VIt.size()-1);
		statii.push_back(curr);
		//export summary data: config_time
		//for (int s = 0; s < (int)timeSwitch.size()-1; s++) {
		//	(*pManData->light_pIofsSummary)
		//		<< (timeSwitch[s] + 1)/60 + 1 // export start time (unit: min)
		//		<< "\t" << timeSwitch[s + 1]/60 // export stop time (unit: min)
		//		<< "\t" << statii[s] << endl; // export light condition
		//}
	}

};
#endif
