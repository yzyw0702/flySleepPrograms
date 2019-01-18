// predict_tube.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include "../../classes/MMacros.hpp"
#include "../../classes/MPredictor.hpp"

void drawRoisWith(Mat& img, vector<Rect>& lRois) {
	for (size_t i = 0; i < lRois.size(); i++){
		rectangle(img, lRois[i], Scalar(0, 0, 255), 2);
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

void mypredict() {
	// create a tube predictor
	//MPredictor* mp1 = new MPredictor;
	MPredictor* mp2 = new MPredictor;
	mp2->loadModel(g_fMu, g_fSigma, g_fTheta1, g_fTheta2);
	// load test image
	//Mat imgBg = imread(g_fBg, CV_LOAD_IMAGE_GRAYSCALE);
	Mat imgSubBg1 = imread(g_fSubBg1, CV_LOAD_IMAGE_GRAYSCALE);
	Mat imgSubBg2 = imread(g_fSubBg2, CV_LOAD_IMAGE_GRAYSCALE);
	// extract tube location maps
	//Mat mapBg = mp1->predict(imgBg);
	vector<Rect> lRoiSubBg1 = mp2->predictOneLine(imgSubBg1);
	vector<Rect> lRoiSubBg2 = mp2->predictOneLine(imgSubBg2);
	//imshow("mapBg", mapBg);
	Mat labelSubBg1; cvtColor(imgSubBg1, labelSubBg1, CV_GRAY2BGR);
	Mat labelSubBg2; cvtColor(imgSubBg2, labelSubBg2, CV_GRAY2BGR);
	drawRoisWith(labelSubBg1, lRoiSubBg1);
	drawRoisWith(labelSubBg2, lRoiSubBg2);
	imshow("labelSubBg1", labelSubBg1);
	imshow("labelSubBg2", labelSubBg2);
	waitKey();
	//imwrite("mapBg.png", mapBg);
	imwrite("labelSubBg1.png", labelSubBg1);
	imwrite("labelSubBg2.png", labelSubBg2);
}

void testPushStack() {
	Mat src = Mat::ones(Size(10, 1),CV_32FC1);
	Mat newone = Mat::zeros(src.size(), CV_8UC1);
	Mat newstruct = Mat::zeros(src.size(), src.type());
	uchar data[] = { -1, -2, -3, -4, -5, -6, -7, -8, -9, 0};
	//src.pop_back();
	uchar* pData = (uchar*)newone.data;
	for (int i = 0; i < newone.cols; i++) {
		pData[i] = data[i];
	}
	float* pNewstruct = (float*)newstruct.data;
	for (int i = 0; i < newstruct.cols; i++) {
		pNewstruct[i] = (float)pData[i];
	}
	src.push_back(newstruct);
	src.push_back(newstruct);
	src.push_back(newstruct);
	src.push_back(newstruct);
	hconcat(Mat::ones(src.rows,1,src.type()), src, src);
	printMat("src",src);
}

int main(int argc, char** argv) {
	mypredict();
	return 0;
}
