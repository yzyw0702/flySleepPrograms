//===========================
//====>  MPredictor
//===========================
#include <iostream>
#include <fstream>
using namespace std;

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
using namespace cv;

#ifndef _MPREDICTOR_HPP_
#define _MPREDICTOR_HPP_

class MPredictor {
public:                                // interfaces
	/* constructor */
	MPredictor() {
	}

public:
	// ## load model separately
	// # [fMu] file containing vector of mean among pixel features
	// # [fSigma] file containing vector of standard deviation among pixel features
	// # [fTheta1] file containing the transformation from input layer to hidden layer
	// # [fTheta2] file containing the transformation from hidden layer to output layer
	// # [return] true = load model successfully, elsewise there will be a prompt of error reminder
	bool loadModel(string fMu, string fSigma, string fTheta1, string fTheta2) {
		// open all file handlers
		ifstream hMu(fMu, ios::in);
		ifstream hSigma(fSigma, ios::in);
		ifstream hTheta1(fTheta1, ios::in);
		ifstream hTheta2(fTheta2, ios::in);
		// check validity
		if (!(hMu.is_open() && hSigma.is_open() && hTheta1.is_open() && hTheta2.is_open())) {
			cout << "Input model is invalid.\n";
			return false;
		}
		int rows, cols;
		//parse Mu
		getSize(hMu, rows, cols);
		hMu.close(); hMu.open(fMu, ios::in);
		m_mu = Mat::zeros(rows, cols, CV_32FC1);
		getData(hMu, m_mu);
		if (m_mu.rows <= 0 || m_mu.cols <= 0) {
			cout << "Input Mu is invalid: [" << m_mu.rows << "x" << m_mu.cols << "]" << endl;
			return false;
		}
		//parse Sigma
		getSize(hSigma, rows, cols);
		hSigma.close(); hSigma.open(fSigma, ios::in);
		m_sigma = Mat::zeros(rows, cols, CV_32FC1);
		getData(hSigma, m_sigma);
		if (m_sigma.rows <= 0 || m_sigma.cols <= 0) {
			cout << "Input Sigma is invalid: [" << m_sigma.rows << "x" << m_sigma.cols << "]" << endl;
		}
		//parse Theta1
		getSize(hTheta1, rows, cols);
		hTheta1.close(); hTheta1.open(fTheta1, ios::in);
		m_theta1 = Mat::zeros(rows, cols, CV_32FC1);
		getData(hTheta1, m_theta1);
		cout << "Input Theta1: [" << m_theta1.rows << "x" << m_theta1.cols << "]" << endl;
		//parse Theta2
		getSize(hTheta2, rows, cols);
		hTheta2.close(); hTheta2.open(fTheta2, ios::in);
		m_theta2 = Mat::zeros(rows, cols, CV_32FC1);
		getData(hTheta2, m_theta2);
		cout << "Input Theta2: [" << m_theta2.rows << "x" << m_theta2.cols << "]" << endl;
		// close
		hMu.close();
		hSigma.close();
		hTheta1.close();
		hTheta2.close();
		return true;
	}
	
	// ## predict tube locations in one line
	// # [imgGray]: input image
	// # [modelWin]: size of slide window in model
	// # [wRoi]: width of slide window in [imgGray]
	// # [return]: list of tube rois in [imgGray] coordinates
	vector<Rect> predictOneLine(Mat& imgGray, Size modelWin = Size(10, 100), int wRoi = 16) {
		// determine convolution image size
		int wT = imgGray.cols;  // target image size
		int hT = imgGray.rows;
		int wS = modelWin.width;  // default slide window size in model
		int hS = modelWin.height;
		int wR = wRoi;  // original slide roi size in imgGray
		int hR = hT;
		int wM = wT - wR + 1;  // conv-map size
		int hM = 1;
		// linearize & en-stack every sub-image within slide window
		Mat imgStack = Mat::zeros(Size(wS*hS, 1), CV_32FC1);
		Mat newone = Mat::zeros(Size(wS*hS, 1), CV_32FC1);
		imgStack.pop_back();  // pop useless data
		Mat img32Gray; imgGray.convertTo(img32Gray, CV_32FC1);
		Rect roi(0,0,0,0);
		Mat sub32Gray;
		// pack all sub-images to convolute
		int stepsize = 1;
		float* pMuData = (float*)m_mu.data;
		float* pSigmaData = (float*)m_sigma.data;
		float* pNewData = (float*)newone.data;
		for (int y = 0; y < 1; y += stepsize) {
			for (int x = 0; x < wM; x += stepsize) {
				roi = Rect(x, y, wR, hR);  // define current slide window
				sub32Gray = img32Gray(roi);
				resize(sub32Gray, sub32Gray, Size(wS, hS));
				float* pData = (float*)sub32Gray.data;  // linearize
				for (int i = 0; i < wS * hS; i++) {  // copy into temporary buffer
					pNewData[i] = (pData[i] - pMuData[i]) / pSigmaData[i];
				}
				for (int i = 0; i < stepsize;i++)
					imgStack.push_back(newone);  // push into stack
			}
		}
		// feedforward
		Mat a1 = feedForward(imgStack, m_theta1);
		Mat y = feedForward(a1, m_theta2);
		// transform y to convolution map
		Mat mapConv = Mat::zeros(Size(wM, hM), CV_8UC1);
		uchar* pMap = (uchar*)mapConv.data;  // get map data pointer
		float* pY = (float*)y.data;  // get y data pointer
		for (int i = 0; i < hM*wM; i++) {
			pMap[i] = max(0.0f, 125 + 125 * pY[i * 2 + 1] - 125 * pY[i * 2]);
		}
		// refine the convolution map
		threshold(mapConv, mapConv, 10, 255, CV_THRESH_OTSU);
		morphologyEx(mapConv, mapConv, CV_MOP_DILATE, Mat());
		// locate bounding boxes of tubes
		vector<int> lCenters = get1dCenters(mapConv);
		vector<Rect> lRois;
		Rect prev(-1000,0,0,0), curr;
		int offset = 0;  // the matching procedure already compensates this offset, so it is 0
		for (size_t i = 0; i < lCenters.size(); i++){
			curr = Rect(offset + lCenters[i], 0, wR, hR);
			if (isEqual(curr, prev)) {  // solve redundant roi
				lRois.pop_back();  // remove last roi
				curr = Rect((curr.x + prev.x) / 2, 0, wR, hR);
			}
			lRois.push_back(curr);  // same height as that of imageGray, but width equals to that of slidewindow
			prev = curr;  // set this as previous roi
		}
		return lRois;
	}

	// ## draw several tube lines, and they will be processed one-by-one
	// # [imgGray] input grayscale image, which may contain multiple tube lines
	// # [modelWin] size of slide window in model
	// # [wRoi]: width of slide window in each tube line within [imgGray]
	// # [return]: list of tube rois in [imgGray] coordinates
	vector<Rect> predictMultipleLine(Mat& imgGray, Size modelWin = Size(10, 100), int wRoi = 16) {
		// This part is complete in another place: see Single Tracer v.4.0
		// loop: ask to draw a large rectangle, and use predictOneLine to automatically detect tubes
		// stop: when enter <esc>; continue: when enter <space>
		// adjust: let user to remove useless rois
		// summarize: add offset for each roi and return all roi in one list
	}


private:  // helper for parse() interface
	vector<string> split(string& src, char delim = ' ') {
		int iL = 0, iR = 0;
		vector<string> ret;
		while (src[iL] == delim) {  // jump all delims at left space
			iL++;
		}
		for (int i = iL; i < src.size(); i++) {  // traverse all char
			if (src[i] == delim) {  // delim found
				iR = i;  // set right marker
				ret.push_back(src.substr(iL, iR - iL));  // split current word
				iL = i + 1;  // set left marker to current position
			}
		}
		if (src[src.size() - 1] != delim) {  // add last one if it's not a delim
			ret.push_back(src.substr(iL, src.size() - iL));
		} return ret;
	}

	void getSize(ifstream& ifs, int& rows, int& cols) {
		string line;
		while (getline(ifs, line)) {
			int pos = -1;
			pos = line.find("rows");
			if (pos != -1) { // find row number
				rows = atoi(line.substr(pos + 6, line.length() - pos - 6).c_str());
			}
			pos = line.find("columns");
			if (pos != -1) { // find row number
				cols = atoi(line.substr(pos + 9, line.length() - pos - 9).c_str());
			}
		}
	}

	void getData(ifstream& ifs, Mat& m) {
		int h = m.rows;  // get data length
		int w = m.cols;
		string line; while (getline(ifs, line)) {  // pass all property lines
			if (line[0] != '#') { break; }
		}
		float val;
		int idx = 0;
		float* pData = (float*)m.data;
		while (1) {
			vector<string> dat = split(line);
			for (size_t i = 0; i < dat.size(); i++) {
				val = (float)atof(dat[i].c_str());
				pData[idx] = val;
				idx++;
			}
			if (!getline(ifs, line)) break;  // read line until end
		}
	}

	void printMat(const char* name, Mat& m, int nRows = -1) {
		int w = m.cols;
		int h = m.rows;
		if (nRows > 0) h = min(m.rows, nRows);
		float* pData = (float*)m.data;
		cout << "matrix <" << name << ">:" << endl;
		for (int y = 0; y < h; y++){
			cout << "< row-start > ";
			for (int x = 0; x < w; x++) {
				cout << pData[x + y*w] << " ";
			} cout << "< row-end >" << endl;
		} cout << endl;
	}
	
	vector<int> get1dCenters(Mat& map) {  // locate center of continuous signal zone in a 1D line
		vector<int> lCenters;
		int start, stop;
		bool inZone = false;
		uchar* pData = map.data;
		for (int i = 0; i < map.rows * map.cols; i++) {
			if (pData[i] == 255) {  // check if current one is a
				if (!inZone) {  // label as start point if previously not in zone
					start = i;
					inZone = true;
				}
				else {  // extend zone width if in zone
					stop = i;
				}
			}
			else if (inZone){  // summarize current zone data and reset switch
				lCenters.push_back((start + stop) / 2);
				inZone = false;
			}
		}
		return lCenters;
	}

	bool isEqual(Rect& a, Rect& b) {
		bool equal = false;
		equal = (abs(a.x - b.x) < a.width);
		return equal;
	}

private:  // FFN operations
	Mat feedForward(Mat& X, Mat& A) {  // [ones(m,1), X] * A'
		Mat bX;  hconcat(Mat::ones(X.rows, 1, CV_32FC1), X, bX);
		Mat z = bX * A.clone().t();
		return sigmoid(z);
	}

	Mat sigmoid(Mat& z) {  // logistic function
		Mat eval; exp(-z, eval);
		Mat a; divide(1, 1 + eval, a);
		return a;
	}
	
private:  // model parameters
	public:
	Mat m_mu;
	Mat m_sigma;
	Mat m_theta1;
	Mat m_theta2;

};
#endif
