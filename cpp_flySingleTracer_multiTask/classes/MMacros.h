#include <opencv2\core\core.hpp>
#include <opencv2\highgui\highgui.hpp>
#include <opencv2\imgproc\imgproc.hpp>
#include <opencv2\gpu\gpu.hpp>
#include <deque>
#include <fstream>
#include <iostream>
#include <string>
#include <ppl.h>
#include <io.h>
#include <time.h>
#include "MPathTool.hpp"
#include "MStringTool.hpp"

#ifndef _MMACROS_H_
#define _MMACROS_H_
#pragma warning( disable : 4996)

//MVideoManager
const int mod_video_cps = 1;

//MVideoManager
const char* fListClips = "list.txt";
const char* wTest = "testWindow";

//MDynamicGrBg
const int mod_dynamic_length = 200;

//MRectRoi
#define MOD_HIGHLIGHT_OFF 0
#define MOD_HIGHLIGHT_ON 1
#define MOD_HIGHLIGHT_EDIT 2

//MRectRoiManager
#define MOD_ADDROI_STOP 0
#define MOD_ADDROI_CONTINUE 1
#define MOD_ADDROI_DELETE 2

#define MOD_SORT_ROW_AFTER_COL 0
#define MOD_SORT_COL_AFTER_ROW 1

//MSingleTracer
const int mod_trace_thresh = 30;
#define MOD_TRACE_FG_WHITE 0
#define MOD_TRACE_FG_BLACK 1

//MPredictor
const char* mod_predict_mu = "Mu.txt";
const char* mod_predict_sigma = "Sigma.txt";
const char* mod_predict_Theta1 = "Theta1.txt";
const char* mod_predict_Theta2 = "Theta2.txt";

//LENGTH
#define MOD_LENGTH_NEAR 5
#define MOD_LENGTH_NUDGE 2

//LABEL
const int mod_label_scale = 5;

#endif
