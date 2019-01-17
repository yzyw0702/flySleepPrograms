#ifndef _MRECTROI_HPP_
#define _MRECTROI_HPP_

#include "MMacros.h"
using namespace cv;
using namespace std;

// annoucements
void onDrawRectRoi(int event, int x, int y, int flags, void * param);

class MRectRoi {
public:
	Rect dynData; // changing rect for preview
	Rect stcData; // current fixed rect
	int xlimit; // uplimit of x
	int ylimit; // uplimit of y
	Point ptCtrl[2]; // control points on drawing
	bool isOnDraw; // switch to reshape rect
	Scalar color; // color for labeling

private:
	void copyFrom(MRectRoi& mrr) {
		this->stcData.x = mrr.stcData.x;
		this->stcData.y = mrr.stcData.y;
		this->stcData.width = mrr.stcData.width;
		this->stcData.height = mrr.stcData.height;
		this->xlimit = mrr.xlimit;
		this->ylimit = mrr.ylimit;
		this->color = mrr.color;
	}

public:
	void init() {
		dynData = Rect(0, 0, 0, 0);
		stcData = Rect(0, 0, 0, 0);
		xlimit = INT_MAX;
		ylimit = INT_MAX;
		ptCtrl[0] = Point(0, 0);
		ptCtrl[1] = Point(0, 0);
		isOnDraw = false;
	}

	MRectRoi(){
		init();
	}

	MRectRoi(int x, int y, int w, int h) {
		init();
		stcData = Rect(x, y, w, h);
	}

	MRectRoi(MRectRoi& mrr) {
		copyFrom(mrr);
	}

public:
	// reshape this rectangle
	int setRoi(
		const char* wPreview,
		Mat& imgPreview
		) {
		// reject command if preview image is invalid
		if(imgPreview.cols < 10) {
			cout << "preview image provided is invalid!\n";
			return 27;
		}
		// set mouse callback
		setMouseCallback(wPreview, onDrawRectRoi, (void*)this);
		// interactive loop
		Mat cpyPreview;
		int key = -1;
		// set uplimit of control points
		xlimit = imgPreview.cols;
		ylimit = imgPreview.rows;
		while (1) {
			// input key
			key = waitKey(1);
			if (key == ' ' || key == 27)
				break;
			// refresh canvas
			cpyPreview = imgPreview.clone();
			// draw dynamic rect on copy preview
			if(isOnDraw) {
				rectangle(cpyPreview, dynData, Scalar(0, 0, 255), 1);
			} else {
				rectangle(cpyPreview, dynData, Scalar(0, 0, 255), 1);
			}
			// show
			imshow(wPreview, cpyPreview);
		}
		return key;
	}

private: // internal op
	// restrict roi range within image
	void restrictRoiWithinRange(){
		if(dynData.x < 0) {
			dynData.x = 0;
		}
		if(dynData.y < 0) {
			dynData.y = 0;
		}
		if(dynData.x + dynData.width >= xlimit) {
			dynData.width = xlimit - dynData.x;
		}
		if(dynData.y + dynData.height >= ylimit) {
			dynData.height = ylimit - dynData.y;
		}
	}

public:
	Rect getRect() {
		return stcData;
	}

public: // interactive operations in call-back
	// modify preview rectangle data
	void reshapeRect() {
		dynData.x = min(ptCtrl[0].x, ptCtrl[1].x);
		dynData.y = min(ptCtrl[0].y, ptCtrl[1].y);
		dynData.width = abs(ptCtrl[0].x - ptCtrl[1].x);
		dynData.height = abs(ptCtrl[0].y - ptCtrl[1].y);
		restrictRoiWithinRange();
	}

	// save current rectangle data
	void saveRect() {
		this->reshapeRect();
		stcData.x = dynData.x;
		stcData.y = dynData.y;
		stcData.width = dynData.width;
		stcData.height = dynData.height;
	}

};


void onDrawRectRoi(int event, int x, int y, int flags, void * param) {
	// get data pointer
	MRectRoi* pRect = (MRectRoi*) param;

	// ask for control points
	switch(event) {
	case CV_EVENT_LBUTTONDOWN:
		// set switch to reshape on
		pRect->isOnDraw = true;
		// set 1st control point
		pRect->ptCtrl[0] = Point(x,y);
		// set 2nd control point
		pRect->ptCtrl[1] = Point(x,y);
		// reshape preview data
		pRect->reshapeRect();
		break;
	case CV_EVENT_LBUTTONUP:
		// set switch to reshape off
		pRect->isOnDraw = false;
		// set 2nd control point
		pRect->ptCtrl[1] = Point(x,y);
		// set current rect data fixed
		pRect->saveRect();
		break;
	default:
		// if on drawing
		if(pRect->isOnDraw) {
			// set 2nd control point
			pRect->ptCtrl[1] = Point(x,y);
			// reshape preview data
			pRect->reshapeRect();
		}
	}
}

#endif