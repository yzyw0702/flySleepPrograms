//===========================
//====>  MSingleTask
//===========================
#include "MMacros.h"
#include "MVideoManager.hpp"
#include "MDataManager.hpp"
#include "MRectRoiManager.hpp"
#include "MLightMonitor.hpp"
#include "MDynamicGrBgManager.hpp"
#include "MTracerManager.hpp"
using namespace std;
using namespace cv;

#ifndef _MSINGLETASK_HPP_
#define _MSINGLETASK_HPP_

class MSingleTask {
public: // constructor
	MSingleTask() {
		_rootPath = ".\\";
		_fClips = "list.txt";
		_fConfig = "config.yaml";
		_pathClips = _rootPath + _fClips;
		_pData = NULL;
		_pClips = NULL;
		_pRois = NULL;
		_pLit = NULL;
		_pBg = NULL;
		_pTracers = NULL;
		_isStop = false;
		_iStartClip = -1;
		_iStartFr = -1;
		_iStopClip = -1;
		_iStopFr = -1;
		_nTtlFr = -1;
	}

public: // init
	void initWith(
		string& rootPath, int callPerSec = 1, bool useAutoDetect = true, 
		int iStartClip = -1, int iStartFr = -1, int iStopClip = -1, int iStopFr = -1, bool isRefineRois = false
	) {
	/* parse input path */
		_rootPath = rootPath;
		_pathClips = _rootPath + _fClips;
	/* init data manager */
		_pData = new MDataManager;
		_pData->initRootPath(_rootPath.c_str());
		_pData->initIOFiles();
	/* init and input video clips */
		_pClips = new MVideoManager(_rootPath.c_str());
		_pClips->initFromDeNovo();
	/* set start-stop time point */
		_iStartClip = iStartClip;
		if (_iStartClip == -1)
			_iStartClip = 0;
		_iStartFr = iStartFr;
		if (_iStartFr == -1)
			_iStartFr = 0;
		if (_iStopClip != -1)
			_iStopClip = iStopClip;
		else
			_iStopClip = INT_MAX;
		if(_iStopFr != -1)
			_iStopFr = iStopFr;
		else
			_iStopFr = INT_MAX;
		_nTtlFr = _pClips->getLength() - _iStartFr - _iStartClip * _pClips->getFps() * 2 * 3600;
		_pClips->resetTimer(iStartClip, iStartFr);
	/* init Roi manager */
		_pRois = new MRectRoiManager;
		_pClips->readPerCall(_imgFr);
		if (useAutoDetect) {
			cout << "using auto detection of tube rois.\n";
			_pRois->initAutoRoiSeriesWith(_imgFr);
		}
		else {
			cout << "Edit roi settings without auto-detection.\n";
			if(!_pRois->importConfig(_pData) || isRefineRois)
				_pRois->initRoiSeriesWith(_imgFr);
		}
	/* init light monitor */
		_pLit = new MLightMonitor;
		_pLit->importConfig(_pData);
		_pLit->setReference(_imgFr);
	/* init background */
		_pBg = new MDynamicGrBgManager;
		_pBg->initWith(_pClips);
	/* init tracers */
		_pTracers = new MTracerManager;
		_pTracers->importConfig(_pData);
		_pTracers->setTracerWith(_pRois, _imgFr, _pBg->clone());
	/* export roi config */
		_pData->resetConfigFile(); // previous configuration data all swapt from here
		_pRois->exportConfig(_pData);
	/* export bg config */
		_pBg->exportConfig(_pData);
	/* export light monitor config */
		_pLit->exportConfig(_pData);
	/* export tracer config */
		_pTracers->exportConfig(_pData);
	/* ask how many frames should be traced */
		_pClips->setCps(callPerSec);
		_pClips->resetTimer(iStartClip, iStartFr);
	}

	void initByGpuWith(string& rootPath, int callPerSec = 1) {
	/* parse input path */
		_rootPath = rootPath;
		_pathClips = _rootPath + _fClips;
	/* init data manager */
		_pData = new MDataManager;
		_pData->initRootPath(_rootPath.c_str());
		_pData->initIOFiles();
	/* init and input video clips */
		_pClips = new MVideoManager(_rootPath.c_str());
		_pClips->initFromDeNovo();
	/* init Roi manager */
		_pRois = new MRectRoiManager;
		Mat _imgFr; _pClips->readPerCall(_imgFr);
		_pRois->importConfig(_pData);
		_pRois->initRoiSeriesWith(_imgFr);
	/* init light monitor */
		_pLit = new MLightMonitor;
		_pLit->importConfig(_pData);
		_pLit->setReference(_imgFr);
	/* init background */
		_pClips->resetTimer();
		_pBg = new MDynamicGrBgManager;
		_pBg->initByGpuWith(_pClips);
		//_pBg->initWith(_pClips);
	/* init tracers */
		_pTracers = new MTracerManager;
		_pTracers->importConfig(_pData);
		_pTracers->setTracerWith(_pRois, _imgFr, _pBg->clone());
	/* export roi config */
		_pData->resetConfigFile(); // previous configuration data all swapt from here
		_pRois->exportConfig(_pData);
	/* export bg config */
		_pBg->exportConfig(_pData);
	/* export light monitor config */
		_pLit->exportConfig(_pData);
	/* export tracer config */
		_pTracers->exportConfig(_pData);
	/* ask how many frames should be traced */
		_pClips->setCps(callPerSec);
		_pClips->resetTimer();
	}

	bool computeNextFrame() { // return true = continue; false = stop
		int iCurrClip, iCurrFr;
		_pClips->getTime(iCurrClip, iCurrFr);
		if (_isStop // stop when command forces it to stop
			|| (iCurrClip >= _iStopClip && iCurrFr >= _iStopFr ) // stop at the defined stop 
			|| !_pClips->readPerCall(_imgBuff)) { // stop if no frame could be read
			stop();
			return false;
		} _imgFr = _imgBuff.clone(); // clone from frame buffer
		if (_imgFr.rows*_imgFr.cols == 0) { // jump if current frame is empty
			return true;
		}
		_pTracers->detect(_imgFr, _pBg->getBg()); // detect targets, compute location & speed
		_pBg->renew(_imgFr); // renew background
		_pLit->computeI(_pTracers->getImgFrGr()); // compute light intensity
		_pClips->getTime(_iClip, _iFr); // get time point
		return true;
	}

	bool computeNextFrameByGpu() { // return true = continue; false = stop
		if (_isStop || !_pClips->readPerCall(_imgBuff)) { // stop at the end
			stop();
			return false;
		} _imgFr = _imgBuff.clone(); // clone from frame buffer
		if (_imgFr.rows*_imgFr.cols == 0) { // jump if current frame is empty
			return false; }
		_pTracers->detectByGpu(_imgFr, _pBg->getGBg()); // detect targets, compute location & speed
		_pBg->renewByGpu(_imgFr); // renew background
		_pLit->computeIByGpu(_pTracers->getGFrGr()); // compute light intensity
		_pClips->getTime(_iClip, _iFr); // get time point
		return true;
	}

	void writeData() {
		/* write data */
		_pClips->writeData(_pData); // write indices of frame played
		_pTracers->writeData(_pData); // write location & speed
		_pLit->writeData(_pData); // write light intensity data
	}

	void labelWith(Mat& imgLabel) {
		imgLabel = _imgFr.clone();
		_pTracers->labelOn(imgLabel, _iClip, _iFr); // label trace
	}

	void reportProgress() {
		if (_iFr % 1000 == 0) {
			cout << "====> Task [" << _rootPath << "]: ";
			cout << "Clip #" << _iClip << " Fr #" << _iFr / 1000
				<< "k, Progress ~= " << (int)((float)((_iClip - _iStartClip) * 2 * 3600 * _pClips->getFps() + _iStartFr + _iFr) / _nTtlFr * 100) << "%" << endl;
		}
	}

	void stop() {
		if (_isStop) return; // only stop if not
		/* export video config */
		_pClips->exportConfig(_pData);
		/* close and clean */
		_pLit->exportSummary(_pData);
		_pData->exportSummary();
		_pData->closeIOFiles();
		_isStop = true;
	}

	bool isStop() {
		return _isStop;
	}

	void release() {
		delete _pData;
		delete _pClips;
		delete _pRois;
		delete _pLit;
		delete _pBg;
		delete _pTracers;
	}

	string getRootPath() {
		return _rootPath;
	}

private: // config members
	string _rootPath;
	string _fClips;
	string _fConfig;
	string _pathClips;
	MDataManager* _pData;
	MVideoManager* _pClips;
	MRectRoiManager* _pRois;
	MLightMonitor* _pLit;
	MDynamicGrBgManager* _pBg;
	MTracerManager* _pTracers;
private: // processing members
	bool _isStop; // flag of whether stopped
	Mat _imgBuff; // video buffer frame
	Mat _imgFr; // video buffer frame copy
	int _iClip; // index of current clip
	int _iFr; // index of current frame
	int _iStartClip;  // clip index to start tracing
	int _iStartFr;  // fr index to start tracing
	int _iStopClip;  // clip index to stop tracing
	int _iStopFr;  // fr index to stop tracing
	int _nTtlFr;  // frame length of clip series
};
#endif
