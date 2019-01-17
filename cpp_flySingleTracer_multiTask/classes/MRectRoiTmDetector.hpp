#include "stdafx.h"
#ifndef _MRECTROITMDETECTOR_HPP_
#define _MRECTROITMDETECTOR_HPP_

#include "MRectRoiManager.hpp"
#include "MGlobalFunc.hpp"

class MRectRoiTmDetector : public MRectRoiManager {
/**** TEMPLATE MATCH OPERATION ****/
private:
	Mat _imgTmpl; //template image
	Mat _mapResult; //Template-Match result
	Vector<Rect> _VRawRoi; //rois detected automatically
	Vector<int> _VScoreRoi; //score reliability of each raw roi

private:
	//evaluation choices
	double L1DistBetween(Mat& I1, Mat& I2) {
		double dist = sum(I1-I2)[0];
		return dist>=0 ? dist : (-dist);
	}

	double L2DistBetween(Mat& I1, Mat& I2) {
		Mat I = (I1 - I2)*255*2/(I1 + I2); multiply(I,I,I);
		return sqrt(sum(I)[0]);
	}

	double mmDiffDistBetween(Mat& I1, Mat& I2) {
		//compute moments
		Moments mm1 = moments(I1);
		Moments mm2 = moments(I2);

		double diff = mm1.mu11/mm1.m00 - mm2.mu11/mm2.m00;
		if(diff > 0) return diff;
		else return -diff;
	}

	double histDistBetween(Mat& I1, Mat& I2) {
		Mat i1,i2;
		I1.convertTo(i1,CV_32FC1);
		I2.convertTo(i2,CV_32FC1);
		return compareHist(i1,i2,CV_COMP_CHISQR);
	}

	//evaluation connector
	double distBetween(Mat& I1, Mat& I2) {
		Mat i1, i2;
		normalize(I1,i1,255);
		normalize(I2,i2,255);
		return histDistBetween(i1,i2);
	}

public:
	bool tm_setTemplate(Mat& img) {
		//check and reset
		if(getWindow().c_str() == NULL) return false;
		this->clearAll();

		//set interactive mode
		this->turnToManagerMode();

		Mat cpCpBg=img.clone();

		//interactive loop
		while(waitKey(33)!=27) {
			//refresh image
			cpCpBg = img.clone();

			//clear previous roi
			if(this->getSize() > 1)
				this->remove(0);
		
			//respond
			this->respondOnImage(cpCpBg,
				drawRect,mouseOverV,mouseInsideR,
				LButtonDownOnV,LButtonDownOnR);

			//report
			imshow(getWindow(),cpCpBg);
		} destroyWindow(getWindow());

		//save template image
		_imgTmpl = img((Rect)*getRoi(0)).clone();
		clearAll();
		return true;
	}
	
	int tm_detect(Mat& target) {
		//prepare result map
		_mapResult = Mat(
			target.cols - _imgTmpl.cols + 1,
			target.rows - _imgTmpl.rows + 1,
			CV_32FC1
			);

		//prepare parameters for match template
		Mat cpTarget,lbTarget;
		int prevThreshGrey = 0, currThreshGrey = 225;
		int prevThreshDist = 0, currThreshDist = 15;
		int prevOffsetX = 0, currOffsetX = MOD_LENGTH_NUDGE;
		int prevOffsetY = 0, currOffsetY = MOD_LENGTH_NUDGE;

		//prepare GUI for match template
		const char* wMatch = "template matching";
		namedWindow(wMatch,CV_WINDOW_NORMAL);
		createTrackbar("threshGrey",wMatch,&currThreshGrey,255);
		createTrackbar("threshDist",wMatch,&currThreshDist,_imgTmpl.cols*_imgTmpl.rows/10);
		createTrackbar("offsetX",wMatch,&currOffsetX,_imgTmpl.cols);
		createTrackbar("offsetY",wMatch,&currOffsetY,_imgTmpl.rows);
		vector<Mat> contours;
		Mat hierarchy;

		while( waitKey(33) != 27 ) {
			if(    currThreshGrey != prevThreshGrey 
				|| currThreshDist != prevThreshDist
				|| currOffsetX != prevOffsetX
				) {
				//reset
				_VRawRoi.clear();
				//no template offset cause it is subtracted by (roi center - roi LeftTop-vertice)
				cpTarget = target.clone();
				lbTarget = target.clone();

				//match
				matchTemplate(cpTarget,_imgTmpl,_mapResult,CV_TM_CCORR_NORMED);
				_mapResult = _mapResult * 255;
				_mapResult.convertTo(_mapResult,CV_8UC1);

				//find contours
				threshold(_mapResult,_mapResult,(double)currThreshGrey,255,CV_THRESH_BINARY);
				findContours(_mapResult,contours,hierarchy,0,2);

				//get candidate rect roi
				clearAll();
				Rect rc;
				int dist;
				for(int i=0;i<(int)contours.size();i++) {
					//get contour bb
					rc = boundingRect(contours[i]);
					
					//adjust bb offset & scale
					rc.x += currOffsetX;
					rc.y += currOffsetY;
					rc.width = _imgTmpl.cols;
					rc.height = _imgTmpl.rows;

					//rule out rois crossing image edges
					if(rc.x < 0 || rc.y < 0) continue;
					if(rc.x+rc.width > target.cols || rc.y+rc.height > target.rows) continue;

					//rule out rois beyond distance threshold
					if( (dist = (int)distBetween(target(rc),_imgTmpl)) < currThreshDist*100 ) continue;

					//save roi candidates
					_VRawRoi.push_back( rc );
					_VScoreRoi.push_back(dist);
					rectangle(lbTarget,_VRawRoi[_VRawRoi.size()-1],Scalar::all(0),2);
				}

			}

			//report and refresh
			imshow(wMatch,lbTarget);
			prevThreshGrey = currThreshGrey;
			prevThreshDist = currThreshDist;
		} destroyWindow(wMatch);

		//add into library
		for(int i=0;i<(int)_VRawRoi.size();i++) {
			add(_VRawRoi[i]);
		}

		//sort order
		return 1;
	}
	


};


#endif