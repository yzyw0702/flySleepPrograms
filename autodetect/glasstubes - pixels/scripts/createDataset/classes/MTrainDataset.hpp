//===========================
//====>  MTrainDataset
//===========================
#include "MMacros.hpp"
#ifndef _MTRAINDATASET_HPP_
#define _MTRAINDATASET_HPP_
#pragma warning(disable:4996)

string getValidDir(string& p) {
	char word = p[p.size() - 1];
	if (word != '\\' && word != '/') {
		p = p + "/";
	} return p;
}

bool isValidPath(string& p) {
	ifstream ifs(p, ios::binary);
	bool ret = ifs.is_open();
	ifs.close();
	return ret;
}

struct MTrainDataset {
	/* [member] original source */
	vector<Mat> m_VImgTubes;  // list of scaled dataset images
	vector<Mat> m_VImgCntrl;  // list of scaled cntrl images

	/* [member] formated dataset */
	string m_dirDataset;  // directory of dataset

	/* <interface> parse source list */
	void initWith(const char* fSrc) {
		/* init parameters */
		ifstream ifs(fSrc, ios::in);  // open source list
		string currDir; string currPathWhole; string currPathRoi;  // task directory; image file path; roi configuration file path
		FileStorage hRoi;  // roi configuration file handler
		Mat currImgWhole;  // current whole image
		Rect currRoi;  // temporary roi buffer
		vector<int> tmpLInt;  // integar array [4]
		char tmpSIndex[64];  // intermediate index of input parameter

		/* traverse all source data */
		while (getline(ifs,currDir)) {  // for each path
			/* parse current task path */
			currDir = getValidDir(currDir);  // make sure there is a '/' or '\\'
			/* load current task image */
			currPathWhole = currDir + "bg.png";  // get original whole image
			if (!isValidPath(currPathWhole)) {
				currPathWhole = currDir + "background.png";  // somtimes need to change name and retry
				if (!isValidPath(currPathWhole)) {  // check if still non-exist
					cout << "[" << currDir << "] "  // omit this task and continue
						 << "Invalid background image"
						 << endl; continue;
				}
			} else {
				currImgWhole = imread(currPathWhole, CV_LOAD_IMAGE_GRAYSCALE);  // load whole image of glass tubes
			}
			/* load current task roi list */
			currPathRoi = currDir + "config.yaml";  // get configuration file path
			if (!isValidPath(currPathRoi)) {  // check if not exist
				cout << "[" << currDir << "] "  // omit this task and continue
					 << "Invalid roi configuration"
					 << endl; continue;
			} else {
				hRoi.open(currPathRoi, FileStorage::READ);  // open configuration file
				int nRoi; hRoi["count_box"] >> nRoi;  // load roi number
				for (int i = 0; i < nRoi; i++) {  // for each roi
					sprintf(tmpSIndex, "roi_%d", i);  // get current roi index
					hRoi[tmpSIndex] >> tmpLInt;  // read into an integar buffer[4]
					currRoi = Rect(tmpLInt[0], tmpLInt[1], tmpLInt[2], tmpLInt[3]);
					m_VImgTubes.push_back(currImgWhole(currRoi));  // save current glass tube image
					currRoi = Rect(
						max(1,tmpLInt[0] - tmpLInt[2]),
						max(1,tmpLInt[1] - tmpLInt[3]/5),
						tmpLInt[2], tmpLInt[3]);  // get negative control by shifting a little bit
					m_VImgCntrl.push_back(currImgWhole(currRoi));  // save current control image
				} hRoi.release();
			}
		} ifs.close();
	}

	/* <interface> create and reformat dataset */
	bool create(const char* dirDst, int wImg, int hImg) {
		/* get destination directory */
		m_dirDataset = getValidDir(string(dirDst));
		/* save and reformat all images */
		Mat currImg;  // current to-do image
		char currSName[128];  // current image name
		ofstream ofsFormatedPos(m_dirDataset + "dataset-pos_formated.txt", ios::out);  // file saving postive formated data
		ofstream ofsFormatedNeg(m_dirDataset + "dataset-neg_formated.txt", ios::out);  // file saving negative formated data
		for (size_t i=0; i < m_VImgTubes.size(); i++) {  // for each image
			sprintf(currSName, "%spos-%d_ori.png", m_dirDataset.c_str(), i);  // name it
			currImg = m_VImgTubes[i];  // copy it
			resize(currImg, currImg, Size(wImg, hImg));  // rescale it
			imwrite(currSName, currImg);  // save it
			for (int j=0; j < wImg * hImg; j++) {  // reformat it
				ofsFormatedPos << int(currImg.data[j]) << "\t";
			} ofsFormatedPos << endl;

			sprintf(currSName, "%sneg-%d_ori.png", m_dirDataset.c_str(), i);  // name it
			currImg = m_VImgCntrl[i];  // copy it
			resize(currImg, currImg, Size(wImg, hImg));  // rescale it
			imwrite(currSName, currImg);  // save it
			for (int j = 0; j < wImg * hImg; j++) {  // reformat it
				ofsFormatedNeg << int(currImg.data[j]) << "\t";
			} ofsFormatedNeg << endl;

		} ofsFormatedPos.close(); ofsFormatedNeg.close();
		return true;
	}

	/* <interface> enhance dataset by mirror flip */
	bool enhance(const char* dirDst, int wImg, int hImg) {
		/* get destination directory */
		m_dirDataset = getValidDir(string(dirDst));
		/* save and reformat all images */
		Mat currImg;  // current to-do image
		Mat currEnhImg;  // current enhanced image
		char currSName[128];  // current image name
		ofstream ofsFormatedPos(m_dirDataset + "dataset-pos_enhanced_formated.txt", ios::out);  // file saving formated data
		ofstream ofsFormatedNeg(m_dirDataset + "dataset-neg_enhanced_formated.txt", ios::out);  // file saving formated data
		for (size_t i=0; i < m_VImgTubes.size(); i++) {  // for each image
			/* treat positive images */
			currImg = m_VImgTubes[i];  // copy it
			resize(currImg, currImg, Size(wImg, hImg));  // rescale it
			/* flip up<->down */
			flip(currImg, currEnhImg, 0);  // flip up-down
			sprintf(currSName, "%spos-%d_fud.png", m_dirDataset.c_str(), i);  // name it
			imwrite(currSName, currEnhImg);  // save it
			for (int j = 0; j < wImg * hImg; j++) {  // reformat it
				ofsFormatedPos << int(currEnhImg.data[j]) << "\t";
			} ofsFormatedPos << endl;
			/* flip left<->right */
			flip(currImg, currEnhImg, 1);  // flip left-right
			sprintf(currSName, "%spos-%d_flr.png", m_dirDataset.c_str(), i);  // name it
			imwrite(currSName, currEnhImg);  // save it
			for (int j = 0; j < wImg * hImg; j++) {  // reformat it
				ofsFormatedPos << int(currEnhImg.data[j]) << "\t";
			} ofsFormatedPos << endl;
			/* flip both up<->down and left<->right */
			flip(currImg, currEnhImg, -1);  // flip left-right
			sprintf(currSName, "%spos-%d_fudlr.png", m_dirDataset.c_str(), i);  // name it
			imwrite(currSName, currEnhImg);  // save it
			for (int j = 0; j < wImg * hImg; j++) {  // reformat it
				ofsFormatedPos << int(currEnhImg.data[j]) << "\t";
			} ofsFormatedPos << endl;

			/* treat negative images */
			currImg = m_VImgCntrl[i];  // copy it
			resize(currImg, currImg, Size(wImg, hImg));  // rescale it
			/* flip up<->down */
			flip(currImg, currEnhImg, 0);  // flip up-down
			sprintf(currSName, "%sneg-%d_fud.png", m_dirDataset.c_str(), i);  // name it
			imwrite(currSName, currEnhImg);  // save it
			for (int j = 0; j < wImg * hImg; j++) {  // reformat it
				ofsFormatedNeg << int(currEnhImg.data[j]) << "\t";
			} ofsFormatedNeg << endl;
			/* flip left<->right */
			flip(currImg, currEnhImg, 1);  // flip left-right
			sprintf(currSName, "%sneg-%d_flr.png", m_dirDataset.c_str(), i);  // name it
			imwrite(currSName, currEnhImg);  // save it
			for (int j = 0; j < wImg * hImg; j++) {  // reformat it
				ofsFormatedNeg << int(currEnhImg.data[j]) << "\t";
			} ofsFormatedNeg << endl;
			/* flip both up<->down and left<->right */
			flip(currImg, currEnhImg, -1);  // flip left-right
			sprintf(currSName, "%sneg-%d_fudlr.png", m_dirDataset.c_str(), i);  // name it
			imwrite(currSName, currEnhImg);  // save it
			for (int j = 0; j < wImg * hImg; j++) {  // reformat it
				ofsFormatedNeg << int(currEnhImg.data[j]) << "\t";
			} ofsFormatedNeg << endl;
		} ofsFormatedPos.close(); ofsFormatedNeg.close();
		return true;
	}
	
	/* constructor */
	MTrainDataset() {
	}

};
#endif
