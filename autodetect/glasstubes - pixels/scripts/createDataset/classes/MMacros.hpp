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
/* dataset parameters */
const int g_wImage = 10;  // width of the image
const int g_hImage = 100;  // height of the image
const int g_lenSingleData = g_wImage * g_hImage;  // data matrix width

#endif
