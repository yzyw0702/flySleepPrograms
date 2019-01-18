//===========================
//====>  MMacros.h
//===========================
#include <iostream>
#include <fstream>
using namespace std;

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
using namespace cv;
#ifndef _MMACROS_HPP_
#define _MMACROS_HPP_
/* file and path */
const char* g_fSrcData = "E:/kanbox/computer science/training_projects/glasstubes - pixels/1-1_listsrc.txt";  // [file] original source
const char* g_dirDstData = "E:/kanbox/computer science/training_projects/glasstubes - pixels/data";  // [path] formated data
/* model path */
const char* g_fBg = "E:/kanbox/computer science/training_projects/glasstubes - pixels/scripts/predict/bg.png";
const char* g_fSubBg1 = "E:/kanbox/computer science/training_projects/glasstubes - pixels/scripts/predict/subbg1.png";
const char* g_fSubBg2 = "E:/kanbox/computer science/training_projects/glasstubes - pixels/scripts/predict/subbg2.png";
const char* g_fMu = "E:/kanbox/computer science/training_projects/glasstubes - pixels/scripts/predict/Mu.txt";
const char* g_fSigma = "E:/kanbox/computer science/training_projects/glasstubes - pixels/scripts/predict/Sigma.txt";
const char* g_fTheta1 = "E:/kanbox/computer science/training_projects/glasstubes - pixels/scripts/predict/Theta1.txt";
const char* g_fTheta2 = "E:/kanbox/computer science/training_projects/glasstubes - pixels/scripts/predict/Theta2.txt";
/* dataset parameters */
const int g_wImage = 10;  // width of the image
const int g_hImage = 100;  // height of the image
const int g_lenSingleData = g_wImage * g_hImage;  // data matrix width

#endif
