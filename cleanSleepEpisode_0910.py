import os
import re
import numpy as np
import h5py


def extractFeature(s, pattern):
	lTerm = re.findall(pattern, s)
	if len(lTerm) < 1:
		return None
	sNum = lTerm[0]
	return sNum.split('\t')


def cvtList2Num(l):
	lRes = []
	for i in l:
		if len(i) == 0:
			lRes.append(-1) # label empty cell as -1
		else:
			lRes.append(float(i))
	return lRes


def extractData(line):
	name, id = line.split('\t')[:2]
	name = name.rstrip(':')
	id = int(id)
	# find number list
	lBoutNum = extractFeature(line, '^[A-Za-z0-9-:]+\t.*endNumber')
	if lBoutNum == None:
		return name, id, [], [], []
	lBoutNum = cvtList2Num(lBoutNum[2:-1])
	lBoutDuration = cvtList2Num(extractFeature(line, 'endNumber.*endlength')[1:-1])
	lStageLatency = cvtList2Num(extractFeature(line, 'endlength.*endLatency')[1:-1])
	return name, id, lBoutNum, lBoutDuration, lStageLatency


def subList(lData,lSel):
	lRet = []
	for i,b in enumerate(lSel):
		if b:
			lRet.append(lData[i])
	return lRet


def cleanSleepEpisode(f, lSel, nMin=0):
	# input all lines
	h = open(f, 'r')
	lLines = [line.rstrip('\t\r\n') for line in h.readlines()]
	h.close()
	# extract bout/stage info
	lName = []
	lId = []
	lNum = []
	mBoutNum = []
	mBoutDuration = []
	mStageLatency = []
	for iL, line in enumerate(lLines):
		if iL == 0:  # omit the headline
			continue
		name, id, lBoutNum, lBoutDuration, lStageLatency = extractData(line)
		lName.append(name)
		lId.append(id)
		mBoutNum.append(lBoutNum)
		mBoutDuration.append(lBoutDuration)
		mStageLatency.append(lStageLatency)
		lNum.append(len(lBoutNum))
	# list all valid data
	lNum = np.array(lNum)
	if nMin < 1:
		maxN = np.max(lNum)
	else:
		maxN = nMin
	lValid = (lNum>=maxN)
	lValidName = subList(lName,lValid)
	lValidId = subList(lId,lValid)
	mValidBoutNum = subList(mBoutNum,lValid)
	mValidBoutDuration = subList(mBoutDuration,lValid)
	mValidStageLatency = subList(mStageLatency,lValid)
	# save clean data
	fOutput = f[:-4] + '_clean-data-all.txt'
	fOutSel = f[:-4] + '_clean.txt'
	hOut = open(fOutput, 'w')
	hOut.write('name\tid')
	hOutSel = open(fOutSel, 'w')
	hOutSel.write('name\tid\tnight bout number\tday bout number\tnight bout duration\tday bout duration\tnight sleep latency\tday sleep latency')
	for n in range(maxN):
		hOut.write('\tbout_number_%d' % n)
	for n in range(maxN):
		hOut.write('\tbout_duration_%d' % n)
	for n in range(maxN):
		hOut.write('\tstage_latency_%d' % n)
	hOut.write('\n')
	hOutSel.write('\n')
	for i,name in enumerate(lValidName):
		hOut.write('%s\t%d' % (name, lValidId[i]))
		hOutSel.write('%s\t%d' % (name, lValidId[i]))
		for j in mValidBoutNum[i]:
			hOut.write('\t%.0f' % j)
		hOutSel.write('\t%.0f' % mValidBoutNum[i][lSel[0]])
		hOutSel.write('\t%.0f' % mValidBoutNum[i][lSel[1]])
		for j in mValidBoutDuration[i]:
			hOut.write('\t%.4f' % j)
		hOutSel.write('\t%.4f' % mValidBoutDuration[i][lSel[0]])
		hOutSel.write('\t%.4f' % mValidBoutDuration[i][lSel[1]])
		for j in mValidStageLatency[i]:
			hOut.write('\t%.0f' % j)
		hOutSel.write('\t%.0f' % mValidStageLatency[i][lSel[0]])
		hOutSel.write('\t%.0f' % mValidStageLatency[i][lSel[1]])
		hOut.write('\n')
		hOutSel.write('\n')
	hOut.close()


def getAllFiles(rootpath,query):
	fileList = []
	for root, lSubdir, lFile in os.walk(rootpath):
		for f in lFile:
			if query in f:
				fileList.append(os.path.join(root, f))
	return fileList


# read time table from config_time.txt
def readTmMat(fTmMat):
	data = h5py.File(fTmMat, 'r')
	mCtTm = np.array(data['CT_time_list']).T
	mTime = []
	offset = 0
	prevCondition = -1
	for r, row in enumerate(mCtTm):
		currCondition = row[0]
		if r == 0:
			startTm = row[1]
			stopTm = 720 - row[1] + 1
		elif not prevCondition == currCondition:
			startTm = offset + 1
			stopTm = startTm + 719
		else:
			continue
		mTime.append([startTm, stopTm, currCondition])
		offset = stopTm
		prevCondition = currCondition
	mTime = np.array(mTime)
	return mTime


def readStageRange(fCfg):
	hCfg = open(fCfg, 'r')
	start = -1
	stop = 10000
	for i, line in enumerate(hCfg.readlines()):
		if i == 0:
			continue
		sStages = line.rstrip('\r\t\n').split('\t')[-1]
		if not sStages == 'none':
			lStages = sStages.rstrip(',').split(',')
			iL = int(lStages[0])
			iR = int(lStages[-1])
			if start < iL:
				start = iL
			if iR < stop:
				stop = iR
	hCfg.close()
	return start-1, stop-1


def selectOptimalStages(fTmMat, fCfgFly):
	mTime = readTmMat(fTmMat)
	iStart, iStop = readStageRange(fCfgFly)
	condition0 = mTime[0, 2]
	nStages = len(mTime)
	if iStart % 2 == 1:
		condition0 = 1 - condition0
		iStart = np.max(0, iStart - 1)
	if condition0 == 0: # if initial condition is dark phase
		if nStages < 4 - iStart:
			return None # stop computing episode
		elif nStages > 6 - iStart: # if duration is long enough
			return [4 - iStart,5 - iStart] # compute the data at third night and third day
		else: # not long enough, but still contain a dark-light phase
			return [2 - iStart,3 - iStart]
	else: # if initial condition is light phase
		if nStages < 3 - iStart:
			return None # stop computing episode
		elif nStages > 7: # if duration is long enough
			return [5 - iStart,6 - iStart]
		elif nStages > 5: # not long enough, but still contain a dark-light phase
			return [3 - iStart,4 - iStart]
		else:
			return [1 - iStart,2 - iStart]


def batchCleanSleepEpisode(rootpath):
	# find all sleepEpisode.txt
	dirBout = 'sleepEpisode'
	fBout = 'sleepEpisode.txt'
	fTm = 'main_SD_R_Addition.mat'
	fCfgFly = 'config_flys.txt'
	fCleanBout = 'sleepEpisode_clean.txt'
	lFIn = getAllFiles(rootpath, fBout)
	lDir = [f[:(0-len(fBout)-1-len(dirBout))] for f in lFIn]
	lFTm = [os.path.join(d, fTm) for d in lDir]
	lFCfgFly = [os.path.join(d, fCfgFly) for d in lDir]
	
	# enumerate all matlab output dirPath
	for iD, dir in enumerate(lDir):
		lSel = selectOptimalStages(lFTm[iD],lFCfgFly[iD])
		print 'computing episode in %s select range = [%d %d]' % (dir, lSel[0], lSel[1])
		nMin = lSel[1]+1  # need at least [nMin] stages data
		pathEpisode = os.path.join(dir, dirBout)
		fOut = os.path.join(pathEpisode, fCleanBout)
		if not os.path.exists(fOut):
			print 'computing episode in %s;' % dir
			cleanSleepEpisode(lFIn[iD], lSel, nMin)
		else:
			print 'episode in %s was already created;' % dir
	# gather all clean episode files togather
	print 'write summary clean-episode file'
	fSumOut = os.path.join(rootpath, fCleanBout)
	hSumOut = open(fSumOut, 'w')
	hSumOut.write('name\tid\tnight bout number\tday bout number\tnight bout duration\tday bout duration\tnight sleep latency\tday sleep latency\n')
	for iD, dir in enumerate(lDir):
		pathEpisode = os.path.join(dir, dirBout)
		fSub = os.path.join(pathEpisode, fCleanBout)
		hSub = open(fSub, 'r')
		hSumOut.writelines(hSub.readlines()[1:])
		hSub.close()
	hSumOut.close()
	if rootpath.rstrip('\\/') == '.':
		print 'summary file is saved at ' + os.getcwd()
	else:
		print 'summary file is saved at ' + rootpath

def test():
	fTmMat = 'main_SD_R_Addition.mat'
	mTime = readTmMat(fTmMat)
	for row in mTime:
		for col in row:
			print '%d\t' % col,
		print '\n'


batchCleanSleepEpisode('.')