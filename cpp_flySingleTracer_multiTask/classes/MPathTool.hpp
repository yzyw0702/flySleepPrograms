#include <io.h>
#include <stdio.h>
#include <iostream>
using namespace std;
#ifndef _MPATHTOOL_HPP_
#define _MPATHTOOL_HPP_

namespace toolpath {
	vector<string> getFiles(string query = "*.avi") {
		// check if such kind of file exists
		_finddata_t fileinfo;
		long hFind = _findfirst(query.c_str(), &fileinfo);
		// if no such file exists, return empty struct and exit
		if (-1 == hFind) {
			cout << "No File for query: " << query << endl;
			return vector<string>();
		}
		// else: enumerate all such files
		vector<string> lFiles;
		lFiles.push_back(string(fileinfo.name));
		while (!_findnext(hFind, &fileinfo)) {
			lFiles.push_back(string(fileinfo.name));
		} _findclose(hFind);
		return lFiles;
	}

	string joinPath(string prefix, string suffix) {
		string result;
		if (prefix[prefix.size() - 1] == '/') {
			return prefix + suffix;
		}
		else {
			return prefix + "/" + suffix;
		}
	}

	bool isFileExist(string f) {
		if ((_access(f.c_str(), 0)) == -1) return false;
		return true;
	}
}

#endif