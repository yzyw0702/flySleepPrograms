
#ifndef _MSINGLETRACER_HPP_
#define _MSINGLETRACER_HPP_

#include "MMacros.h"
using namespace cv;
using namespace std;

class MSingleTracer {
private: //core data
	float _speed; // speed per interval (in pixels)

private: //intermediates
	Mat _imgFgBw; // foreground image
	vector<Mat> _contours;
	Point2f _ptCurr; // current location of target
	Point2f _ptPrev; // previous location of target
	int _areaOfC; //area of current contour
	int _maxAreaOfC; //max area of contour
	int _iMaxC; //index of max contour
	Moments _mmMaxC; //moments of contour with max area

private:
	double distOf(Point2f& prev, Point2f& curr) { // compute 2-points distance
		return sqrt((prev.x - curr.x) * (prev.x - curr.x)
				+ (prev.y - curr.y) * (prev.y - curr.y));
	}
	
	void computeLocation() { // compute target location
		medianBlur(_imgFgBw, _imgFgBw, 3); // remove pepper&salt noise
		_contours.clear(); // clear storage of contours from previous frame
		findContours(_imgFgBw, _contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);
		if (_contours.size() == 0) { // nothing will be detected if target stays
			_speed = 0; // target stop moving
			_ptCurr.x = _ptPrev.x; _ptCurr.y = _ptPrev.y; // keep previous location as current one
			return; // return previous location if nothing detected
		}
		/* filter contours by size */
		_maxAreaOfC = -1; _iMaxC = -1;
		for (int i = 0; i<(int)_contours.size(); i++) { // check areas of all detected contours
			_areaOfC = (int)contourArea(_contours[i]);
			if (_areaOfC > _maxAreaOfC) { // only choose the contour with the largest area
				_maxAreaOfC = _areaOfC; _iMaxC = i;
			}
		}
		/* compute target location */
		_mmMaxC = moments(_contours[_iMaxC]);
		if (_mmMaxC.m00 != 0) { // get location of target
			_ptCurr.x = (float)(_mmMaxC.m10 / (_mmMaxC.m00 + 0.0000001));
			_ptCurr.y = (float)(_mmMaxC.m01 / (_mmMaxC.m00 + 0.0000001));
		}
		else { // failed to compute target center (usual cause: contour is too small)
			_ptCurr.x = _ptPrev.x; _ptCurr.y = _ptPrev.y; // keep previous location as current one
		}
	}

	void computeSpeed() { // compute target speed
		if (_ptPrev.x == -1 && _ptPrev.y == -1) _speed = 0;
		else _speed = (float)distOf(_ptPrev, _ptCurr);
	}

public:
	void initWith(
		Mat& fgBwRoi
		) {
		_imgFgBw = fgBwRoi.clone();
		_ptCurr = Point2f( -1,-1 );
		//computeLocation();
	}

	void detect(Mat& fgBwRoi) { // detect target
		_imgFgBw = fgBwRoi.clone(); // copy the black-white image to find contours
		/* save previous locations */
		_ptPrev.x = _ptCurr.x;
		_ptPrev.y = _ptCurr.y;
		/* compute current location & speed */
		computeLocation();
		computeSpeed();
	}
	
	//get absolute location
	Point2f getAbsLocation(Rect& roi) {
		Point2f offset((float)roi.x, (float)roi.y);
		return _ptCurr + offset;
	}

	//get absolute speed (in mm)
	float getAbsSpeed(float mm2pixel) {
		return _speed * mm2pixel;
	}

};


#endif