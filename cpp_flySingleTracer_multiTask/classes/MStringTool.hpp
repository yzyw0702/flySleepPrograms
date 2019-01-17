//===========================
//====>  MStringTool
//===========================
#include <iostream>
#include <vector>
#include <string>
using namespace std;
#ifndef _MSTRINGTOOL_HPP_
#define _MSTRINGTOOL_HPP_

namespace toolstring {
	void printStringList(vector<string>& v) {
		for (size_t i = 0; i < v.size(); i++) {
			cout << "[" << i << "] = " << v[i] << endl;
		}
	}

	vector<string> split(string& src, char delim = ' ') {
		int iL = 0, iR = 0;
		vector<string> ret;
		while (src[iL] == delim) {  // jump all delims at left space
			iL++;
		}
		for (int i = iL; i < (int)src.size(); i++) {  // traverse all char
			if (src[i] == delim) {  // delim found
				iR = i;  // set right marker
				ret.push_back(src.substr(iL, iR - iL));  // split current word
				iL = i+1;  // set left marker to current position
			}
		}
		if (src[src.size() - 1] != delim) {  // add last one if it's not a delim
			ret.push_back(src.substr(iL, src.size() - iL));
		} return ret;
	}
	
	void rstrip(string& src, char c = ' ') {
		int n = src.size();
		while (src[n - 1] == c && n > 0) n--;
		src = src.substr(0, n);
	}

	void lstrip(string& src, char c = ' ') {
		int n = 0;
		int N = src.size();
		while (src[n] == c && n < N) n++;
		src = src.substr(n, N);
	}
	
	string rstrip(string src, string lpatterns) {
	bool isFinish = false;
	char suffix;
	int iLast = (int)src.size();
	while (!isFinish) {  // clear all the characters listed in lpatterns
		suffix = src[iLast - 1];
		bool isClear = true;
		for (int i = 0; i < (int)lpatterns.size(); i++) {  // check the list lpatters
			if (suffix == lpatterns[i]) {
				iLast--;
				isClear = false;
				break;
			}
		}
		if (isClear || iLast == 0)  // exit only when all listed suffices are cleared
			isFinish = true;
	}
	return src.substr(0, iLast);
	}

	string lstrip(string src, string lpatterns) {
		bool isFinish = false;
		char prefix;
		int iFirst = 0;
		while (!isFinish) {  // clear all the characters listed in lpatterns
			prefix = src[iFirst];
			bool isClear = true;
			for (int i = 0; i < (int)lpatterns.size(); i++) {  // check the list lpatters
				if (prefix == lpatterns[i]) {
					iFirst++;
					isClear = false;
					break;
				}
			}
			if (isClear || iFirst == src.size() - 1)  // exit only when all listed suffices are cleared
				isFinish = true;
		}
		return src.substr(iFirst, src.size());
	}

	template <class T>
	int isInList(vector<T>& list, T query) {
		if (list.size() == 0) return -1;
		for (int i = 0; i < (int)list.size(); i++)
			if (query == list[i]) return i;
		return -1;
	}

	void replace(string& target, string before, string after) {
		string::size_type pos = 0;
		string::size_type nBefore = before.size();
		string::size_type nAfter = after.size();
		while ((pos = target.find(before, pos)) != string::npos) {
			target.replace(pos, nBefore, after);
			pos += nAfter;
		}
	}
};

namespace debug_toolstring {
	using namespace toolstring;

	void debug_split() {
		string s1 = "This is a string list.";
		string s2 = "This is another string list with some bug. ";
		string s3 = " There is a space at first position.";
		string s4 = "     Several left spaces appear. ";
		string s5 = "Several in-between     spaces should be split.";
		string s6 = "use,comma,to,split,this,string,";
		printStringList(split(s1));
		printStringList(split(s2));
		printStringList(split(s3));
		printStringList(split(s4));
		printStringList(split(s5));
		printStringList(split(s6, ','));
	}
};

#endif
