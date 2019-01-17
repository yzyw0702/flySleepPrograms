#ifndef _MDATAMANAGER_HPP_
#define _MDATAMANAGER_HPP_

#include "MMacros.h"
using namespace std;
using namespace cv;

class MDataManager {

public: // stream data collection
	/* file names */
	string data_rootPath;
	string data_fConfig;
	string vid_fTimes;
	string light_fIt;
	string light_fSummary;
	string tracer_fOfsAbsSpeed;
	string tracer_fOfsAbsLocation;
	/* filestream pointers */
	fstream* vid_pIofsTimes; // MVideoManager: output file of clip indices and frIC indices
	fstream* light_pIofsIt; // MLightMonitor: output file of light intensity
	//fstream* light_pIofsSummary; // MLightMonitor: output file of config_time.txt (sections of light conditions)
	ofstream* tracer_pOfsAbsLocation; // MTracerManager: output file of absolute location
	ofstream* tracer_pOfsAbsSpeed; // MTracerManager: output file of absolute speed

public:
	/* CONSTRUCTOR */
	MDataManager() {
		data_rootPath = ".\\";
		setIOFilesInRootPath();
	}

private:
	void createIOFile(fstream* fs, const char* fname) {
		fs->close();
		fs->open(fname, ios::out);
		fs->close();
		fs->open(fname, ios::out | ios::in);
	}

	// init file names with default paths
	void setIOFilesInRootPath() {
		data_fConfig = data_rootPath + "config.yaml";
		vid_fTimes = data_rootPath + "vid_time.txt";
		light_fIt = data_rootPath + "light_intensity.txt";
		//light_fSummary = data_rootPath + "config_time.txt";
		tracer_fOfsAbsSpeed = data_rootPath + "txt.speed";
		tracer_fOfsAbsLocation = data_rootPath + "txt.location";
	}

public:

	// swap previous configure file data
	void resetConfigFile() {
		FileStorage* pfs = new FileStorage(data_fConfig, FileStorage::WRITE);
		//tm tm; time(&tm);
		time_t ttime; time(&ttime);
		tm *tm = localtime(&ttime);
		char sTm[64];
		sprintf(sTm, "%d/%d/%d %d:%d:%d",
			1900 + tm->tm_year, 1 + tm->tm_mon, tm->tm_mday,
			tm->tm_hour, tm->tm_min, tm->tm_sec);
		*pfs << "createTime" << sTm;
		pfs->release();
	}

	// reset fstream pointers
	void resetIOFileStream() {
		vid_pIofsTimes->seekg(ios::beg);
		light_pIofsIt->seekg(ios::beg);
		//light_pIofsSummary->seekg(ios::beg);
	}

	// init specific configure file, use before initIOFiles()
	void initRootPath(
		const char* rootPath
		) {
		data_rootPath = rootPath;
		setIOFilesInRootPath();
		if ((_access(this->data_fConfig.c_str(), 0)) == -1)
			this->resetConfigFile();
	}

	// open output files
	void initIOFiles() {
		// create online data files
		vid_pIofsTimes = new fstream(vid_fTimes, ios::out | ios::in);
		createIOFile(vid_pIofsTimes, vid_fTimes.c_str());
		light_pIofsIt = new fstream(light_fIt, ios::out | ios::in);
		createIOFile(light_pIofsIt, light_fIt.c_str());
		tracer_pOfsAbsLocation = new ofstream(tracer_fOfsAbsLocation, ios::out);
		tracer_pOfsAbsSpeed = new ofstream(tracer_fOfsAbsSpeed, ios::out);
		// create summary data files
		//light_pIofsSummary = new fstream(light_fSummary, ios::out | ios::in);
		//createIOFile(light_pIofsSummary, light_fSummary.c_str());
		// output header
		(*vid_pIofsTimes) << "clip_index\t" << "in-clip_frame_index" << endl;
		(*light_pIofsIt) << "relative_intensity (sum/max)" << endl;
	}

	void exportSummary() { // save end stime
		FileStorage* pfs = new FileStorage(data_fConfig, FileStorage::APPEND);
		//tm tm; time(&tm);
		time_t ttime; time(&ttime);
		tm *tm = localtime(&ttime);
		char sTm[64];
		sprintf(sTm, "%d/%d/%d %d:%d:%d",
			1900 + tm->tm_year, 1 + tm->tm_mon, tm->tm_mday,
			tm->tm_hour, tm->tm_min, tm->tm_sec);
		*pfs << "endTime" << sTm;
		pfs->release();
	}

	// close output files
	void closeIOFiles() {
		vid_pIofsTimes->close();
		light_pIofsIt->close();
		//light_pIofsSummary->close();
		tracer_pOfsAbsLocation->close();
		tracer_pOfsAbsSpeed->close();
	}


//
//
//private:
//
//	//data file pointers
//	
//
//
//private:
//	bool readConfigOfContinue() {
//		//load data file of last stop time
//		if((int)_access_s("traceRange.txt",0 )!=0) return false;
//		ifstream ifs("traceRange.txt");
//
//		//get video index
//		string szVid; ifs >> szVid;
//		vid_iClipOfLast = atoi(szVid.c_str());
//
//		//get frame position
//		string szTime; ifs>>szTime;
//		vid_iFrICOfLast = atoi(szTime.c_str());
//
//		//report
//		cout<<"last time: iVid = "<<vid_iClipOfLast<<", "
//			<<"iFr = "<<vid_iFrICOfLast<<endl;
//
//		ifs.close();
//		return true;
//	}
//
///* SETTINGS */
//
//	void resetDataHolder() {
//		//close new files
//		_pOutputSpeed->close();
//		_pOutputLocation->close();
//		
//		//restore .old data
//		system("del txt.location");
//		system("del txt.speed");
//		system("rename txt.location.old txt.location");
//		system("rename txt.speed.old txt.speed");
//
//		//reopen
//		_pOutputSpeed->open("txt.speed",ios::app);
//		_pOutputLocation->open("txt.location",ios::app);
//	}
//
//	void removeOldData() {
//		system("del txt.location.old");
//		system("del txt.speed.old");
//	}
//
///* OPEN */
//	//open file to save tracing data
//	void openStorageOfTracer(
//		const char* fileSpeed = "txt.speed",
//		const char* fileLocation = "txt.location",
//		const char* fileConfig = "config.yaml"
//		) {
//		//delete all .old files
//		if((int)_access_s("txt.location.old",0)==0)
//			system("del txt.location.old");
//		if((int)_access_s("txt.speed.old",0)==0)
//			system("del txt.speed.old");
//
//		//check if old data is here
//		if((int)_access_s(fileSpeed,0) == 0) { //already exist
//			cout<<"There is already a speed file, it is going to be renamed.\n";
//			char szCommand[64];
//			sprintf_s(szCommand,"rename %s %s.old",fileSpeed,fileSpeed);
//			system(szCommand);
//		}
//
//		//open a new data file
//		_pOutputSpeed->open(fileSpeed,ios::out);
//
//		//check if old data is here
//		if((int)_access_s(fileLocation,0) == 0) { //already exist
//			cout<<"There is already a location file, it is going to be renamed.\n";
//			char szCommand[64];
//			sprintf_s(szCommand,"rename %s %s.old",fileLocation,fileLocation);
//			system(szCommand);
//		}
//
//		//open a new data file
//		_pOutputLocation->open(fileLocation,ios::out);
//
//		//open a new configuration file
//		FileStorage* pFsConfig = new FileStorage;
//		if( !pFsConfig->open(fileConfig,FileStorage::READ) ) {
//			cout<<"New configure file is created!\n";
//			pFsConfig->open(fileConfig,FileStorage::WRITE);
//			pFsConfig->release();
//		}
//		
//		//get last tracing progress
//		vid_iClipOfLast = 0;
//		vid_iFrICOfLast = 0;
//		readConfigOfContinue();
//	}
//
///* WRITE */
//
//	//write tracing range
//	void refreshLatestFr(int iCurrVid, int iCurrFr) {
//		//get data
//		vid_iClipOfLast = iCurrVid;
//		vid_iFrICOfLast = iCurrFr;
//
//		//write into file
//		if(iCurrFr % mod_dynamic_length != 0) return;
//		ofstream ofs("traceRange.txt");
//		ofs<<vid_iClipOfLast<<"\t"
//			<<vid_iFrICOfLast<<endl;
//		ofs.close();
//	}
//
//	//write data onto files
//	void write(vector<float>& speed, vector<Point2f>& location) {
//		for(int i=0;i<(int)speed.size();i++) {
//			*_pOutputSpeed << speed[i] << "\t";
//			*_pOutputLocation << (int)location[i].x << "\t" << (int)location[i].y <<"\t"; 
//		} 
//
//		//turn to next line
//		*_pOutputSpeed<<endl;
//		*_pOutputLocation<<endl;
//	}
//
///* CLOSE */
//	//close file of tracing
//	void closeStorageOfTracer() {
//		_pOutputSpeed->close();
//		_pOutputLocation->close();
//	}
//
};





#endif