import os
import re
import numpy as np


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
			lRes.append(0)
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
	


def run():
	# input raw data
	f = 'D:/video/20180605_circadian-sik2koattp-w_male/20180605_circadian-sik2koattp-w_male/sleepEpisode/sleepEpisode.txt'
	lSel = [11,12]
	nMin = 2  # need at least [nMin] stages data
	cleanSleepEpisode(f, lSel, nMin)


run()