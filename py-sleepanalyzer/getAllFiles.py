from myutils import *
# getAllFiles.m

def getAllFiles(rootpath=None,query=None):
	fileList = []
	for root, lSubdir, lFile in os.walk(rootpath):
		for f in lFile:
			if query in f:
				fileList.append(os.path.join(root, f))
	return fileList