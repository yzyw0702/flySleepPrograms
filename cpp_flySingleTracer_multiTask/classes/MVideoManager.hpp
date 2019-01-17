#ifndef _MVIDEOMANAGER_HPP_
#define _MVIDEOMANAGER_HPP_

#include "MMacros.h"
#include "MDataManager.hpp"
using namespace cv;

class MVideoManager { //singleton
private:
	/* I/O communication with MDataManager */
	string data_rootPath; // root path of video clips, configurations etc.
	vector<string> _VNameClips; // name list of clips
	vector<int> _VLenClips;     // length list of clips
	int _iLastClip;        // index of clip traced last time
	int _iLastFrIC;          // index of frame traced last time (in last clip)
	bool _isStartFromDenovo;    // switch on when start from de novo
	bool _isStartFromLatest;    // switch on when start from latest

	cv::VideoCapture* _pClip;   // video pointer
	int _iFrIC;                 // frame index within current clip
	int _iClip;                 // clip index
	int _cFrIC;                 // frame number of current clip
	int _cTtFr;                 // total frame number of clips
	int _cClips;                // clip number
	int _fps;                   // frame per second
	int _cps;                   // call per second
	int _jump;                  // frames jump per call
	
private: // init operations
	
	// default
	void init_default() {
		data_rootPath = ".\\";

		_iLastClip = 0;
		_iLastFrIC = 0;
		_isStartFromDenovo = false;
		_isStartFromLatest = false;

		_iFrIC = 1;
		_cFrIC = 0;
		_cTtFr = 0;
		_cClips = 0;
		_cps = 1;
		_pClip = new VideoCapture;
	}

	// initialization
	/// <summary>
	/// init data manager
	/// </summary>
	/// <param name="pManData"> data manager pointer </param>
	/// <return> false=failed, true=success </return>
	bool init_with(
		int cps = 1
		) {
		_cTtFr = 0;
		string fListOfClips = data_rootPath + string("list.txt");
		appendVideoSeries(fListOfClips); // load video series
		_pClip = new VideoCapture; // get initial video
		int isContinueFromLast=0;//discuss which time point to start
		//cout<<"Do you want to continue from last tracing progress?\n"
		//	<<"[0=no, 1=yes] Your answer = ";
		//cin>>isContinueFromLast;
		if (isContinueFromLast)
			initFromLatest();
		else
			initFromDeNovo();
		_cClips = (int) _VNameClips.size();//get video info
		_cFrIC = (int) _pClip->get(CV_CAP_PROP_FRAME_COUNT);
		_fps = (int) _pClip->get(CV_CAP_PROP_FPS);
		if(isContinueFromLast)  _iClip = _iLastClip;
		else _iClip = _iLastClip = 0;
		if(isContinueFromLast) {
			_iLastFrIC -= (_iLastFrIC % _fps); // adjust to nearest keyframe
			_iFrIC = max(_iLastFrIC - mod_dynamic_length, 0 ); // reserve a number of frames to compute bg
		} else {
			_iFrIC = _iLastFrIC = 1;
		}
		_cps = cps; // get cps and jump length
		_jump = _fps/_cps - 1;
		if(!_pClip->set(CV_CAP_PROP_POS_FRAMES,_iFrIC)) { // set frame pointer to required position
			cout<<"video pointer failed to reset to "<<_iFrIC<<endl;
		} return true;
	}

public: // constructors
	MVideoManager( const char* rootPath=".\\", int cps=1 ) {
		init_default();
		initRootPath(rootPath);
		init_with(cps);
	}

public: // append operations

	bool appendClip(string& fNameClip) {
		string pathClips = data_rootPath + fNameClip;
		if ((int)_access(pathClips.c_str(), 0) == 0) { //check if exist
			// register this clip
			_VNameClips.push_back(pathClips);

			// collect clip info
			VideoCapture cap(pathClips);
			int currLen = (int)cap.get(CV_CAP_PROP_FRAME_COUNT);
			_VLenClips.push_back(currLen);
			//cout << pathClips << ": successfully loaded.\n";

			// refresh total frame number
			_cTtFr += currLen;

			cap.release();
			return true;
		} else {
			cout << pathClips << ": cannot be accessed.\n";
			return false;
		}
	}

	//bind videos by selection
	void appendVideoSeries(string& fNameClips = string()) {
		//ask list of input video
		string fidxVid; 
		if( fNameClips.size() > 0 )  {
			fidxVid = fNameClips;
		} else {
			cout<<"input video list: ";
			cin>>fidxVid;
		}

		// establish an input file stream
		ifstream fsIdxVid(fidxVid,ios::in);

		//scan list
		string nameVid;
		int cOkLoaded=0,cNotLoaded=0;
		while(getline(fsIdxVid,nameVid)) {
			if(appendClip(nameVid)) {
				cOkLoaded++;
			} else {
				cNotLoaded++;
			}
		}
		cout << "\t" <<cOkLoaded<<" files loaded; " <<cNotLoaded<<" files failed.\n";
	}
	
public: // play operations

	//start a new trace
	void initFromDeNovo() {
		_pClip->open(_VNameClips[0]);
	}

	//continue trace from last time
	void initFromLatest() {
		//set video
		if( (int)_access_s("traceRange.txt",0) != 0 ) {
			initFromDeNovo();
		} else {
			_pClip->open( _VNameClips[_iLastClip] );
		}
	}

public: // set operations

	void initRootPath(const char* rootPath) {
		data_rootPath = rootPath;
	}

	//reset frame pointer
	//## necessary before start tracking
	bool resetTimer(int iClip = -1,int iFrInClip=-1) {
		// set clip idx
		if(iClip >= 0) {
			_iClip = iClip;
		}
		_pClip->release();
		_pClip->open(_VNameClips[_iClip]);
		_cFrIC = _VLenClips[_iClip];
		
		// set frame idx
		if(iFrInClip > 0) {
			_iFrIC = iFrInClip;
		}
		else {
			_iFrIC = 0;
		}
		return _pClip->set(CV_CAP_PROP_POS_FRAMES,_iFrIC);
	}

	bool resetContinuousTimer(int iFr) {
		int cFr = 0;
		for (_iClip = 0; cFr <= iFr; _iClip++) {
			cFr += _VLenClips[_iClip];
		}
		_iClip--; // go back to current clip
		cFr -= _VLenClips[_iClip]; // remove the extra clip length
		_iFrIC = iFr - cFr; // locate exact frame idx in current clip
		_pClip->release(); // reopen clip pointer at this clip, at this frame
		_pClip->open(_VNameClips[_iClip]);
		return _pClip->set(CV_CAP_PROP_POS_FRAMES, _iFrIC);
	}

	//switch to next vieo if required
	//## true: next video is available
	//## false: the end of all videos
	bool setNextVideo() {
		//close current video
		_pClip->release();
		_iClip++;

		//check and set to the next
		if(_iClip < _cClips) { //go to next video
			_iLastClip = _iClip;
			_pClip->open(_VNameClips[_iClip]);
			
			//refresh In-Clip properties
			_cFrIC = (int) _pClip->get(CV_CAP_PROP_FRAME_COUNT);
			_iFrIC = 0;

			return true;
		} else { //the END of clip series
			return false;
		}
	}

public: // get operations

	// write stream
	void writeData(MDataManager* pManData) {
		char data[64];
		sprintf(data,"%d\t%d\n",_iClip,_iFrIC);
		(*pManData->vid_pIofsTimes) << data;
	}

	// export configuration to data manager
	void exportConfig(MDataManager* pManData) {
		FileStorage* pFsConfig = new FileStorage(pManData->data_fConfig, FileStorage::APPEND);
		if(!pFsConfig->isOpened()) { // avoid invalid storage
			cout << "Export vid_config failed!\n";
			return;
		}
		(*pFsConfig) << "vid_iClipOfLast" << _iLastClip;
		(*pFsConfig) << "vid_iFrICOfLast" << _iLastFrIC;
		(*pFsConfig) << "vid_VNameOfClips" << _VNameClips;
		(*pFsConfig) << "vid_VLenOfClips" << _VLenClips;
		(*pFsConfig) << "vid_callPerSeconds" << _cps;

		// instantly save it
		pFsConfig->release();

	}

	//get cps-based frame, change video if necessary
	//## true: frame acquired;
	//## false: reach the video end
	bool readPerCall(Mat& fr){
		//get frame if available
		_pClip->read(fr);
		//get video pointer position
		for(int i=0;i<_jump;i++) {
			if(_iFrIC + i > _cFrIC - _jump + 1) {
				break;
			} _pClip->grab();
		}
		//refresh time
		_iFrIC += 1 + _jump;
		if (_iFrIC >= _cFrIC - _jump + 1) {
			if( !setNextVideo() ) {
				return false;
			}
			cout << "switch to clip: " << _VNameClips[_iClip] << endl;
		} return true;
	}

	void setCps(int cps) {
		_cps = cps;
		_jump = _fps / _cps - 1;
	}

	void setJump(int jump) {
		_jump = jump;
		_cps = _fps / (_jump + 1);
	}

	string getRootPath() {
		return data_rootPath;
	}

	//get call per second
	int getCps() {
		return _cps;
	}

	//get frame per second
	int getFps() {
		return _fps;
	}

	// get total frame number
	int getLength() {
		return _cTtFr;
	}

	//get video pointer
	VideoCapture* getClipPtr() {
		return _pClip;
	}

	//get indices of Video and frame
	void getTime(int& iVid, int& iFr) {
		iVid = _iClip;
		iFr = _iFrIC;
	}

};


#endif