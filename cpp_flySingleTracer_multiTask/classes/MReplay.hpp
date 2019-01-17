//===========================
//====>  MReplay
//===========================
#include "MMacros.h"
#include "MVideoManager.hpp"
using namespace std;
using namespace cv;

#ifndef _MREPLAY_HPP_
#define _MREPLAY_HPP_

class MReplay : public MVideoManager {
public: // constructor
	MReplay(const char* rootPath) : MVideoManager(rootPath) {
		cout << rootPath << endl;
		initReplay();
	}

public: // interfaces

	bool showNextFrame(string& wLabel) { // get current frame and jump to the next
		/* read current frame and go to next frame position */
		string sNextClip, sNextFr;
		int iNextClip;
		int iNextFr;
		if (isUseIfsTime) { // parse data of time line
			*pIfsTime >> sNextClip >> sNextFr;
			iNextClip = atoi(sNextClip.c_str());
			iNextFr = atoi(sNextFr.c_str());
			if (iNextClip == _iCurrClip) { // if within same clip
				this->setJump(iNextFr - _iCurrFr - 1); // jump to position before the destination frame
			}
		}

		int iFr, iClip; this->getTime(iClip, iFr);

		if (!isUseIfsTime) {
			this->getTime(_iCurrClip, _iCurrFr);
		}
		
		bool isNext = this->readPerCall(_imgBuff);

		imgLabel = _imgBuff.clone();
		/* annotate fly location, speed and time point */
		VBuff.clear(); // reset buffer
		getNextLocation(); // get next line data
		labelTime(imgLabel);
		labelLocation(imgLabel);
		if (VPtPrev.size() == _cTargets) {
			getNextSpeed();
			labelSpeed(imgLabel);
		}
		imshow(wLabel, imgLabel);

		if (isUseIfsTime && iNextClip != _iCurrClip) { // if need to switch to next clip
			this->resetTimer(iNextClip, iNextFr); // reopen the video clip and goto next location
		}
		_iCurrClip = iNextClip;
		_iCurrFr = iNextFr;
		return isNext;

	}
	
	bool exportNextFrame(const char* fOutput) { // get current frame and jump to the next
		/* read current frame and go to next frame position */
		string sNextClip, sNextFr;
		int iNextClip;
		int iNextFr;
		if (isUseIfsTime) { // parse data of time line
			*pIfsTime >> sNextClip >> sNextFr;
			iNextClip = atoi(sNextClip.c_str());
			iNextFr = atoi(sNextFr.c_str());
			if (iNextClip == _iCurrClip) { // if within same clip
				this->setJump(iNextFr - _iCurrFr - 1); // jump to position before the destination frame
			}
		}

		int iFr, iClip; this->getTime(iClip, iFr);

		if (!isUseIfsTime) {
			this->getTime(_iCurrClip, _iCurrFr);
		}

		bool isNext = this->readPerCall(_imgBuff);

		imgLabel = _imgBuff.clone();
		/* annotate fly location, speed and time point */
		VBuff.clear(); // reset buffer
		getNextLocation(); // get next line data
		labelTime(imgLabel);
		labelLocation(imgLabel);
		if (VPtPrev.size() == _cTargets) {
			getNextSpeed();
			labelSpeed(imgLabel);
		}
		imwrite(fOutput, imgLabel);

		if (isUseIfsTime && iNextClip != _iCurrClip) { // if need to switch to next clip
			this->resetTimer(iNextClip, iNextFr); // reopen the video clip and goto next location
		}
		_iCurrClip = iNextClip;
		_iCurrFr = iNextFr;
		return isNext;

	}

	void stop() {
		if (isUseIfsTime) {
			pIfsTime->close();
		}
		pIfsLoc->close();
		pIfsSpd->close();
	}

	void startFrom(int iSec) {
		if (isUseIfsTime) {
			seekLine(pIfsTime, iSec * cps + 1); // set time file to target place (head line should be considered)
			seekLine(pIfsLoc, iSec * cps + 1); // set location file to target place
			seekLine(pIfsSpd, iSec * cps + 1); // set speed file to target place
		} else {
			seekLine(pIfsLoc, iSec * cps); // set location file to target place
			seekLine(pIfsSpd, iSec * cps); // set speed file to target place
		}
		if (isUseIfsTime) {
			*pIfsTime >> sWordBuff; _iCurrClip = atoi(sWordBuff.c_str());
			*pIfsTime >> sWordBuff; _iCurrFr = atoi(sWordBuff.c_str());
			this->resetTimer(_iCurrClip, _iCurrFr); // reset player timer
		}
		else {
			this->resetContinuousTimer(iSec * this->getFps());
			this->getTime(_iCurrClip, _iCurrFr);
		}
	}

private: // internal operations

	void initReplay() {
		string rootPath = this->getRootPath(); // set absolute file paths
		fTime = rootPath + "vid_time.txt";
		fLoc = rootPath + "txt.location";
		fSpd = rootPath + "txt.speed";
		pIfsTime = new ifstream(fTime, ios::in); // open stream files
		pIfsLoc = new ifstream(fLoc, ios::in);
		pIfsSpd = new ifstream(fSpd, ios::in);
		if (!pIfsTime->is_open()) {
			cout << "Time file is missing! Use fixed pace to play." << endl;
			isUseIfsTime = false;
		} else {
			isUseIfsTime = true;
		}
		if (!pIfsLoc->is_open() || !pIfsSpd->is_open()) { // check file statii
			cout << "Data file missing at rootPath: " << rootPath << endl;
		}
		if (isUseIfsTime) {
			string head; getline(*pIfsTime, head); // remove the head line
			_iCurrClip = 0; *pIfsTime >> sWordBuff; _iCurrClip = atoi(sWordBuff.c_str());
			_iCurrFr = 0; *pIfsTime >> sWordBuff; _iCurrFr = atoi(sWordBuff.c_str());
			
		} else {
			_iCurrClip = 0;
			_iCurrFr = 0;
		}
		cout << "Enter cps used during tracing = "; cin >> cps;
		this->setCps(cps);
		getNextLocation(); // count number of targets
		pIfsLoc->seekg(ios::beg);
		_cTargets = (int)VPtCurr.size();
		cout << _cTargets << " targets are detected." << endl;
		RNG rng(123456); // generate random color for each target
		for (int i = 0; i < (int)VPtCurr.size(); i++) {
			VColor.push_back(Scalar(rng.uniform(0, 255), rng.uniform(0, 255), rng.uniform(0, 255)));
		}
	}
	
	void getNextLocation() { // parse next line of location
		getline(*pIfsLoc, sLineBuff); // get the first whole line
		stringstream ssIfs(sLineBuff); // split by whitespace
		VBuff.clear(); // reset buffer
		while (ssIfs >> sWordBuff) { // load data
			VBuff.push_back((float)atof(sWordBuff.c_str()));
		}
		VPtPrev = VPtCurr; // save previous locations
		VPtCurr.clear(); // reset current locations
		for (int i = 0; i < VBuff.size() / 2; i++) { // parse location data
			VPtCurr.push_back(Point2f(VBuff[i*2], VBuff[i*2 + 1]));
		}
	}

	void getNextSpeed() { // parse next line of speed
		getline(*pIfsSpd, sLineBuff); // get the first whole line
		stringstream ssIfs(sLineBuff); // split by whitespace
		VSpdPrev = VSpdCurr; // save previous speed
		VSpdCurr.clear(); // reset current speed
		while (ssIfs >> sWordBuff) { // load speed
			VSpdCurr.push_back((float)atof(sWordBuff.c_str()));
		}
	}

	void labelTime(Mat& imgLabel) {
		sprintf(szWordBuff,"iClip=%d, iFr=%d",_iCurrClip, _iCurrFr);
		putText(imgLabel, szWordBuff, Point(10, 30), CV_FONT_HERSHEY_SIMPLEX, 0.8, Scalar(0, 0, 255),2);
	}

	void labelLocation(Mat& imgLabel) {
		if (VPtPrev.size() == _cTargets) { // start to draw moving trace from 2nd frame
			for (int i = 0; i < (int)VPtCurr.size(); i++) {
				line(imgLabel, VPtPrev[i], VPtCurr[i], VColor[i], 1);
			}
		}
		for (int i = 0; i < (int)VPtCurr.size(); i++) {
			circle(imgLabel, VPtCurr[i], 4, VColor[i], 2);
			sprintf(szWordBuff, "%d", i);
			putText(imgLabel, szWordBuff, VPtCurr[i], CV_FONT_HERSHEY_SIMPLEX, 1, VColor[i]);
		}
	}

	void labelSpeed(Mat& imgLabel) {
		for (int i = 0; i < (int)VSpdCurr.size(); i++) {
			circle(imgLabel, VPtCurr[i], 2 * (int)VSpdCurr[i], VColor[i], 4);
		}
	}

	void seekLine(ifstream* pF, int iL) { // seek position before target line
		pF->seekg(ios::beg); // reset position
		string buff;
		for (int i = 0; i < iL; i++) {
			getline(*pF, buff);
		}
	}

private: // members
	int _iCurrClip; // index of current clip
	int _iCurrFr; // index of current frame
	int cps; // fixed cps to play
	string fTime; // file name of time line
	string fLoc; // file name of location
	string fSpd; // file name of speed
	bool isUseIfsTime; // switch of using time infilestream
	ifstream* pIfsTime; // input file of time line
	ifstream* pIfsLoc; // input file of location
	ifstream* pIfsSpd; // input file of speed
	int _cTargets; // number of targets
	Mat _imgBuff; // buffer of current frame
	Mat imgLabel; // image label
	vector<float> VBuff; // buffer list of data
	string sLineBuff; // buffer of line
	string sWordBuff; // buffer of word
	char szWordBuff[64]; // buffer of screen label word
	vector<Scalar> VColor; // list of annotation color
	vector<Point2f> VPtPrev; // list of previous location
	vector<Point2f> VPtCurr; // list of current location
	vector<float> VSpdPrev; // list of previous speed
	vector<float> VSpdCurr; // list of current speed
	

};
#endif
