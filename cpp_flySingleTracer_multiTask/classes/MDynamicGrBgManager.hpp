#ifndef _MDYNAMICGRBGMANAGER_HPP_
#define _MDYNAMICGRBGMANAGER_HPP_

#include "MMacros.h"
#include "MDataManager.hpp"
#include "MVideoManager.hpp"
using namespace cv;
using namespace std;

class MDynamicGrBgManager : public Mat {
private:
	MVideoManager* _pClips;
	int _iFrStart; // start frame to initialize background
	Mat _gr, _gr32, _sum32, _avg32; // cpu single/summed/averaged frame buffer
	gpu::GpuMat _gbg, _gfr, _ggr, _ggr32, _gsum32, _gavg32; // conrresponding gpu frame buffers
	deque<Mat> _QFrGr32; // buffer queue
	deque<gpu::GpuMat> _QGFrGr32; // gpu buffer queue
	int _cQSize; // queue size

public:
	//constructors
	MDynamicGrBgManager() {
		_cQSize = mod_dynamic_length;
	}

	// clear
	void clear() {
		_QFrGr32.clear();
	}

	//set Queue size
	void setQSize(int cQSize) {
		_cQSize = cQSize;
	}
	
	// init background
	bool initWith(MVideoManager* pReader) {
		//check if video has been bound
		if(!pReader) return false;
		_pClips = pReader;
		
		//get video info
		_iFrStart = pReader->getLength();
		int wFr = (int)pReader->getClipPtr()->get(CV_CAP_PROP_FRAME_WIDTH);
		int hFr = (int)pReader->getClipPtr()->get(CV_CAP_PROP_FRAME_HEIGHT);

		//init images
		Mat fr,gr;
		_sum32 = Mat::zeros(Size(wFr,hFr),CV_32FC1);

		//compute initial background
		int iFr=0;
		while(pReader->getClipPtr()->read(fr)&&iFr++<_cQSize) {
			cvtColor(fr,gr,CV_BGR2GRAY);
			gr.convertTo(_gr32,CV_32FC1);
			_QFrGr32.push_back(_gr32.clone());
			_sum32+=_gr32;
		} _avg32 = _sum32 / _cQSize;
		_avg32.convertTo(*this,CV_8UC1);

		return true;
	}

	// init background by gpu
	bool initByGpuWith(MVideoManager* pReader) {
		//check if video has been bound
		if (!pReader) return false;
		_pClips = pReader;

		//get video info
		_iFrStart = pReader->getLength();
		int wFr = (int)pReader->getClipPtr()->get(CV_CAP_PROP_FRAME_WIDTH);
		int hFr = (int)pReader->getClipPtr()->get(CV_CAP_PROP_FRAME_HEIGHT);

		//init images
		Mat fr;
		gpu::GpuMat gfr;
		_sum32 = Mat::zeros(Size(wFr, hFr), CV_32FC1);
		_gsum32.upload(_sum32);

		//compute initial background
		int iFr = 0;
		while (pReader->readPerCall(fr) && iFr++<_cQSize) {
			gfr.upload(fr.clone());
			gpu::cvtColor(gfr, _ggr, CV_BGR2GRAY);
			_ggr.convertTo(_ggr32, CV_32FC1);
			_QGFrGr32.push_back(_ggr32.clone());
			gpu::add(_gsum32, _ggr32, _gsum32);
		} gpu::divide(_gsum32, _cQSize, _gavg32);
		_gavg32.convertTo(_gbg, CV_8UC1);
		_gbg.download(*this);

		return true;
	}

	//save background
	bool exportConfig(MDataManager* pData) {
		char imgName[1024];
		sprintf(imgName, "%sbackground.png", pData->data_rootPath.c_str());
		if (!toolpath::isFileExist(imgName))
			return imwrite(imgName, *this);
		else
			return true;
		
	}

	//refresh background
	void renew(Mat &fr) {
		//update single/summed frame buffer
		cvtColor(fr, _gr, CV_BGR2GRAY);
		_gr.convertTo(_gr32,CV_32FC1);
		_sum32 = _sum32 - _QFrGr32[0] + _gr32;

		//update background
		_avg32 = _sum32 / _cQSize;
		_avg32.convertTo(*this,CV_8UC1);

		//update buffer queue
		_QFrGr32.pop_front();
		_QFrGr32.push_back(_gr32.clone());
	}

	// refresh background by GPU
	void renewByGpu(Mat &fr) {
		_gfr.upload(fr);
		gpu::cvtColor(_gfr, _ggr, CV_BGR2GRAY);
		_ggr.convertTo(_ggr32, CV_32FC1);
		gpu::subtract(_gsum32, _QGFrGr32[0], _gsum32);
		gpu::add(_gsum32, _ggr32, _gsum32);
		gpu::divide(_gsum32, _cQSize, _gavg32);
		_gavg32.convertTo(_gbg,CV_8UC1);
		//_gbg.download(*this);
		_QGFrGr32.pop_front();
		_QGFrGr32.push_back(_ggr32.clone());
	}

	Mat getBg() {
		return *this;
	}

	gpu::GpuMat getGBg() {
		return _gbg;
	}

	//reload background
	bool reload(const char* szLoadName = "background") {
		string loadName = szLoadName;

		//reload configure data
		ifstream ifs(loadName+".config");
		string loadReaderName;
		ifs>>loadReaderName
			>>_iFrStart
			>>_cQSize;

		//reload buffer queue
		setQSize(_cQSize);
		_QFrGr32.clear();
		initWith(_pClips);

		ifs.close();
		return true;
	}

};


#endif