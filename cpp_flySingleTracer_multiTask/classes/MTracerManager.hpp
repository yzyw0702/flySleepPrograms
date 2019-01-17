#ifndef _MTRACERMANAGER_HPP_
#define _MTRACERMANAGER_HPP_

#include "MMacros.h"
#include "MSingleTracer.hpp"
#include "MRectRoiManager.hpp"
#include <opencv2\gpu\gpu.hpp>

using namespace cv;
using namespace std;
using namespace Concurrency;

void onSetScale(int event, int x, int y, int flags, void* param);

class MTracerManager {
private:
	Vector<MSingleTracer*> _VTracers; // tracer array
	MRectRoiManager* _pManRoi; // roi manager
	float _scaleMm2pixel; // scale of length in mm v.s. pixels
	int _ruleOfDetect; // rule of determining which target: white or black
	int _thresh; // threshold of bw image

private:
	gpu::GpuMat _gFr;
	gpu::GpuMat _gFrGr;
	gpu::GpuMat _gBgGr;
	gpu::GpuMat _gFgGr;
	gpu::GpuMat _gFgBw;
	Mat _imgFrGr;
	Mat _imgBgGr;
	Mat _imgFgGr;
	Mat _imgFgBw;

private:
	Vector<float> _VAbsSpeed; // absolute speed (mm instead of pixel) in one frame
	Vector<Point2f> _VAbsLocation; // absolute location (relative location + offset) in one frame

public: // parameters for interactive operations in callback functions
	Mat _imgLabelScale;
	bool isDrawLine;
	Point pt[2];

private: // internal operations
	double distOf(Point& prev, Point& curr) {
		return sqrt(
			(prev.x - curr.x) * (prev.x - curr.x)
			+ (prev.y - curr.y) * (prev.y - curr.y)
			);
	}

	void computeForeground(Mat& srcFr, Mat& srcBgGr) {
		cvtColor(srcFr, _imgFrGr, CV_BGR2GRAY);
		if (_ruleOfDetect == MOD_TRACE_FG_WHITE) { // white target, black background
			_imgFgGr = _imgFrGr - srcBgGr;
		}
		else { // black target, white background
			_imgFgGr = srcBgGr - _imgFrGr;
		}
		threshold(_imgFgGr, _imgFgBw, _thresh, 255, CV_THRESH_BINARY);
	}

	void computeForegroundByGpu(Mat& srcFr, gpu::GpuMat& srcGBgGr) {
		_gFr.upload(srcFr);
		gpu::cvtColor(_gFr, _gFrGr, CV_BGR2GRAY);
		if (_ruleOfDetect == MOD_TRACE_FG_WHITE) { // white target, black background
			gpu::addWeighted(_gFrGr, 1, srcGBgGr, -1, 0, _gFgGr);
		}
		else { // black target, white background
			gpu::addWeighted(srcGBgGr, 1, _gFrGr, -1, 0, _gFgGr);
		}
		gpu::threshold(_gFgGr, _gFgBw, _thresh, 255, CV_THRESH_BINARY);
		_gFgBw.download(_imgFgBw);
	}

public:

	MTracerManager() {
		_scaleMm2pixel = 0;
	}
	
	void importConfig(MDataManager* pManData) {
		FileStorage* pfs = new FileStorage(pManData->data_fConfig, FileStorage::READ);
		(*pfs)["scaleMm2pixel"] >> _scaleMm2pixel;
		pfs->release();
	}

	void exportConfig(MDataManager* pManData) {
		FileStorage* pfs = new FileStorage(pManData->data_fConfig, FileStorage::APPEND);
		(*pfs) << "scaleMm2pixel" << _scaleMm2pixel;
		pfs->release();
	}

	void setTracerWith(
		MRectRoiManager* pManRoi,
		Mat& imgFirstFr,
		Mat& imgBgGr,
		int thresh = mod_trace_thresh,
		int method = MOD_TRACE_FG_WHITE) { // set roi, bg, interval and mm:pixel ratio
		/* parse input parameters */
		_pManRoi = pManRoi;
		_imgBgGr = imgBgGr.clone();
		_ruleOfDetect = method;
		_thresh = thresh;
		/* interactive loop: define mm:pixel ratio */
		if (_scaleMm2pixel <= 0) { // create a new ratio if couldn't loaded
			/* init interactive environment for defining scale */
			const char* wSetScale = "Draw a line to compute ratio of mm:pixel; press [Esc] to confirm";
			namedWindow(wSetScale, CV_WINDOW_NORMAL);
			setMouseCallback(wSetScale, onSetScale, this);
			isDrawLine = false;
			cvtColor(_imgBgGr, _imgLabelScale, CV_GRAY2BGR); // get copy of reference image
			Mat cpLabelScale;
			while (waitKey(1) != 27) {
				cpLabelScale = _imgLabelScale.clone();
				line(cpLabelScale, pt[0], pt[1], Scalar(0, 0, 255), 2);
				imshow(wSetScale, cpLabelScale); // preview line on image
			} destroyWindow(wSetScale);
			/* compute the scale of mm:pixel */
			float lenReal;
			cout << "enter the length of the line (in mm): ";
			cin >> lenReal;
			_scaleMm2pixel = lenReal / (float)distOf(pt[0], pt[1]);
			cout << "ratio of mm:pixel = " << _scaleMm2pixel << endl;
		}
		/* compute the first foreground black-white image */
		computeForeground(imgFirstFr, _imgBgGr);
		/* init single tracers */
		Rect roi;
		for (int i = 0; i < _pManRoi->getSize(); i++) {
			MSingleTracer* pTracer = new MSingleTracer; // init every detector
			roi = _pManRoi->getRoi(i)->getRect();
			pTracer->initWith(_imgFgBw(roi)); // init roi-bg of this tracer
			_VTracers.push_back(pTracer); // register this detector
		}
	}

	// get intermediate image
	Mat getImgFrGr() {
		return _imgFrGr;
	}

	gpu::GpuMat getGFrGr() {
		return _gFrGr;
	}

	//detect targets in every roi
	void detect(Mat& imgFr, Mat& imgBgGr) {
		_imgBgGr = imgBgGr.clone();
		computeForeground(imgFr, _imgBgGr);
		parallel_for( 0,(int)_VTracers.size(),[&](int i) {
			_VTracers[i]->detect(_imgFgBw(_pManRoi->getRoi(i)->getRect()).clone());
		});
	}

	//detect targets in every roi
	void detectByGpu(Mat& imgFr, gpu::GpuMat& gBgGr) {
		computeForegroundByGpu(imgFr, gBgGr);
		parallel_for(0, (int)_VTracers.size(), [&](int i) {
			_VTracers[i]->detect(_imgFgBw(_pManRoi->getRoi(i)->getRect()).clone());
		});
	}
	
	//label targets
	void labelOn(Mat& imgLabel,int iVid,int iFr){
		//label index and location
		MRectRoi *mrr;
		Rect roi;
		Point2f ptAbs;
		char szIdx[64];
		for(int i=0;i<(int)_VTracers.size();i++) {
			mrr = _pManRoi->getRoi(i);
			roi = mrr->getRect();
			ptAbs = _VTracers[i]->getAbsLocation(roi);
			circle(imgLabel, ptAbs, 4, mrr->color, 2);
			sprintf(szIdx, "%d", i);
			putText(imgLabel, szIdx, ptAbs, CV_FONT_HERSHEY_SIMPLEX, 1, mrr->color);
		}
		//label time point
		char szTime[32];
		sprintf_s(szTime,"#%d clip, #%d fr",iVid,iFr);
		putText(
			imgLabel,szTime,Point(imgLabel.cols - 250, imgLabel.rows - 10),
			CV_FONT_HERSHEY_SIMPLEX,0.5,Scalar(0,0,255)
			);
	}

	//write data on disk
	void writeData(MDataManager* pManData){
		ofstream *pLoc = pManData->tracer_pOfsAbsLocation; // get location file pointer
		ofstream *pSpd = pManData->tracer_pOfsAbsSpeed; // get speed file pointer
		Point2f loc;
		float spd;
		for (int i = 0; i<(int)_VTracers.size(); i++) { // write data for each fly
			loc = _VTracers[i]->getAbsLocation(_pManRoi->getRoi(i)->getRect()); // compute absolute location
			spd = _VTracers[i]->getAbsSpeed(_scaleMm2pixel); // compute absolute speed (mm/sec)
			*pLoc << loc.x << "\t" << loc.y << "\t"; // write absLocation
			*pSpd << spd << "\t"; // write absSpeed
		} *pLoc << endl; *pSpd << endl; // turn to next line
	}

};

void onSetScale(int event, int x, int y, int flags, void* param) {
	//get pointer
	MTracerManager *pMan = (MTracerManager*) param;

	//execute mouse commands
	switch(event) {
	case CV_EVENT_LBUTTONDOWN:
		pMan->isDrawLine = true;
		pMan->pt[0] = Point(x,y);
		pMan->pt[1] = Point(x,y);
		break;
	case CV_EVENT_LBUTTONUP:
		pMan->isDrawLine = false;
		break;
	default:
		if(pMan->isDrawLine == true) {
			pMan->pt[1] = Point(x,y);
		}
	}
}







#endif