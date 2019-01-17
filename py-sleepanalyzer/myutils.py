# coding=utf-8
import os
import tkFileDialog
import uniout
import numpy as np
import cv2
import scipy.io as sio


def Chinese(s):
	return unicode(s, 'utf-8')


def lenSpdFile(f):
	nL = 0
	h = open(f, 'r')
	for l in h.readlines():
		nL+=1
	h.close()
	return nL


def headOf(mData, iRow, title):
	ret = ''
	ret += '......matrix %s, head line =\n' % title
	for v in mData[iRow]:
		ret += '%.3f, ' % v
	ret += '\n'
	return ret


def printOdrTable(lStkName, llOdr):
	ret = ''
	for i, lOdr in enumerate(llOdr):
		ret += '%s %d -> %d; ' % (lStkName[i], lOdr[0], lOdr[-1])
	ret += '\n'
	return ret


def getAllFiles(rootpath=None,query=None):
	fileList = []
	for root, lSubdir, lFile in os.walk(rootpath):
		for f in lFile:
			if query in f:
				fileList.append(os.path.join(root, f))
	return fileList


def getRelativePath(rootpath, query):
	relativePath = ''
	for i,c in enumerate(query):
		if i < len(rootpath) and c == rootpath[i]:
			continue
		relativePath += c
	if relativePath[0] == '/' or relativePath[0] == '\\':
		return relativePath[1:]
	else:
		return relativePath


def printReport(fReport, msg):
	hReport = open(fReport, 'a')
	hReport.write(msg)
	hReport.close()
	print msg,


def uigetdir(cwd, title):
	dir = tkFileDialog.askdirectory(initialdir = cwd, title=title)
	return dir


# read time table from config_time.txt
def readTime(fTime, fReport):
	hTime = open(fTime, 'r')
	mTime = []
	for line in hTime.readlines():
		if len(line.rstrip('\t\r\n')) == 0:
			continue
		lVal = [int(v) for v in line.rstrip('\t\r\n').split('\t')]
		mTime.append(lVal)
	hTime.close()
	mTime = np.array(mTime)
	# check validity and return the time table
	if isCfgTimeValid(mTime, fReport):
		return mTime
	else: # if invalid
		return np.array([])


def isCfgTimeValid(mTime, fReport):
	# check if time table start from 1
	if not mTime[0,0] == 1:
		msg = '...[config_time.txt] the 1st line should start from 1'
		printReport(fReport, msg)
		return False
	# after stage 1, check whether each stage's duration and continuity
	for i in range(2,len(mTime)):
		if mTime[i,1] - mTime[i,0] > 719:  # duration <= 720
			msg = '...[config_time.txt] in line %d stage duration is beyond 720min.\n' % (i + 1)
			printReport(fReport, msg)
		if not mTime[i,0] - mTime[i - 1,1] == 1:  # continuity
			msg = '...[config_time.txt] in line %d time is not continuous.\n' % (i + 1)
			printReport(fReport, msg)
	return True


def readOrder(fOdr, fReport):
	hOdr = open(fOdr, 'r')
	llOdr = []
	lStkName = []
	for line in hOdr.readlines():
		if len(line) < 1:
			continue
		stkName, slIdx = line.rstrip('\r\n').split('\t')
		lIdx = [int(v) for v in slIdx.split(',')]
		llOdr.append(lIdx)
		lStkName.append(stkName)
	return lStkName, llOdr


def importMat(f): # read chunk data file, its data-type is float
	m = []
	with open(f) as h:
		for line in h:
			m.append([float(v) for v in line.rstrip('\t\r\n').split('\t')])
	return np.array(m)


def drawRasterPlot(lmRasterPlot, outputDir):
	nChn = len(lmRasterPlot)
	for iChn in range(nChn):
		stkName = lmRasterPlot[iChn][0].rstrip(':')
		fOutRasterPlot = os.path.join(outputDir, '%d--%s.jpeg' % (iChn+1, stkName))
		if os.path.exists(fOutRasterPlot):
			continue
		dataSlp = lmRasterPlot[iChn][1]
		mSlp = dataSlp[:, 1:]
		nTm, nFly = np.shape(mSlp)
		nRows = nFly * 60 + 70 # 行高 60 pixel，最后空余1行绘制光照分布
		imgRasterPlot = np.zeros((nRows, nTm)) + 1 # 绘制8位图片，背景为白色
		for iFly in range(nFly):
			for iPix in range(60+1): # 当前果蝇的睡眠标记为黑色，高低表示一分钟睡了多久
				imgRasterPlot[iFly * 60 + iPix, mSlp[:, iFly] > 60 - iPix] = 0
		for iPix in range(60):
			imgRasterPlot[ - iPix - 1, :] = dataSlp[:, 0] # 绘制光照条件轴
		imgRasterPlot *= 255
		cv2.imwrite(fOutRasterPlot, imgRasterPlot)


def summaryData(lFIn, fOutPrefix, inname, outname):
	lData = []
	fOut = fOutPrefix + outname + '.mat'
	if os.path.exists(fOut):
		print '.........%s already exists.' % fOut
		return True
	print '.........saveing data %s.' % fOut
	for iChn, fMat in enumerate(lFIn):
		data = None
		try:
			data = sio.loadmat(fMat)
		except(MemoryError):
			print '.........out of memory when packing data ' + outname
			if not data == None:
				for k in data.keys():
					del data[k]
			return False
		lData.append(data[inname])
		for k in data.keys():
			del data[k]
	try:
		sio.savemat(fOut, {outname:lData})
	except(MemoryError):
		del lData
		print '.........out of memory when summarizing data ' + fOut
		return False
	return True


def saveSummaryData(pathMat):
	lFIn = getAllFiles(pathMat,'main-py_SD_R_ch')
	fOutPrefix = os.path.join(pathMat, 'main-py_SD_R_raw_')
	# 重组数据
	nTotalStk = 0
	fOutNStk = fOutPrefix + 'nStk.mat'
	if not os.path.exists(fOutNStk):
		for iChn, fMat in enumerate(lFIn):
			data = sio.loadmat(fMat)
			nTotalStk += data['nStk']
			for k in data.keys():
				del data[k]
		sio.savemat(fOutNStk, {'nStk':nTotalStk})
	else:
		print '.........%s already exists.' % fOutNStk
	isOk = False
	isOk = summaryData(lFIn, fOutPrefix,'mSpd', 'lmSpd')
	if not isOk:
		return False
	isOk = summaryData(lFIn, fOutPrefix,'lStkName', 'llStkName')
	if not isOk:
		return False
	isOk = summaryData(lFIn, fOutPrefix,'lOdr', 'llOdr')
	if not isOk:
		return False
	isOk = summaryData(lFIn, fOutPrefix,'mRest', 'lmRest')
	if not isOk:
		return False
	isOk = summaryData(lFIn, fOutPrefix,'mRestMinutes', 'lmRestMinutes')
	if not isOk:
		return False
	isOk = summaryData(lFIn, fOutPrefix,'mSleep30MinSD', 'lmSleep30MinSD')
	if not isOk:
		return False
	isOk = summaryData(lFIn, fOutPrefix,'mSleep30MinCT', 'lmSleep30MinCT')
	if not isOk:
		return False
	isOk = summaryData(lFIn, fOutPrefix,'mSpdFine', 'lmSpdFine')
	if not isOk:
		return False
	isOk = summaryData(lFIn, fOutPrefix,'mSpd30MinCT', 'lmSpd30MinCT')
	if not isOk:
		return False
	return True


def readSummaryData(pathMat, name):
	fPrefix = os.path.join(pathMat, 'main-py_SD_R_raw_')
	retData = None
	data = sio.loadmat(fPrefix + name + '.mat')
	retData = data[name]
	return retData


def summaryOf(name, mat):
	return '......%s.shape = %d x %d x %d\n' % (name, len(mat), len(mat[0]), len(mat[0][0]))