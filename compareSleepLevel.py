import numpy as np
import pandas as pd
import os


def stripEmptyColumns(df):  # filter place-holder (-1) columns and invalid (NaN) columns
	lValidCol = []
	for col in df.columns:
		if list(df[col])[0] == 'NaN':
			continue
		if list(df[col])[0] >= 0:
			lValidCol.append(col)
	return df[lValidCol]


def readSleepCurvePair(fBef, fAft):
	# read matlabSD.m output as input
	dfBef = pd.read_table(fBef, header=None)
	dfAft = pd.read_table(fAft, header=None)
	# remove empty and invalid columns
	dfValidBef = stripEmptyColumns(dfBef)
	dfValidAft = stripEmptyColumns(dfAft)
	# get the whole list of stock names
	lName = list(dfBef[0])
	lName = sorted(set(lName), key=lName.index)  # remove redundancy
	dfFltrBef = pd.DataFrame(columns=dfValidBef.columns)
	dfFltrAft = pd.DataFrame(columns=dfValidAft.columns)
	for i, name in enumerate(lName):
		subBef = dfValidBef[dfValidBef[0]==name]
		subAft = dfValidAft[dfValidAft[0]==name]
		for id in list(subBef[1]):
			if id in list(subAft[1]):
				dfFltrBef = pd.concat([dfFltrBef, subBef[subBef[1]==id]])
				dfFltrAft = pd.concat([dfFltrAft, subAft[subAft[1]==id]])
	# for group 'after': only reserve the first 24-hr data-set
	lFltr = dfFltrAft.columns
	return dfFltrBef, dfFltrAft[np.concatenate([np.array([0,1]),lFltr[2:50]])]


def readAliveFlyList(fConfig, pattern):
	df = pd.read_table(fConfig)
	# filter lines containing 'frag'-label same as $pattern
	lLabel = []
	for term in df['frag']:
		if pattern in term:
			lLabel.append(True)
		else:
			lLabel.append(False)
	# remove '--' at column 'line'
	fValidConfig = fConfig[:-4] + '_valid.txt'
	df[lLabel].to_csv(fValidConfig, sep='\t', index=False)
	fRefConfig = fValidConfig[:-4] + '-ref.txt'
	hValidConfig = open(fValidConfig, 'r')
	hRefConfig = open(fRefConfig, 'w')
	for i,line in enumerate(hValidConfig.readlines()):
		if i == 0:
			hRefConfig.write(line)
			continue
		if '--' in line:
			hRefConfig.write(line.split('--')[1])
	hRefConfig.close()
	hValidConfig.close()
	dfRefConfig = pd.read_table(fRefConfig)
	return dfRefConfig


def getAliveDataset(dfData, dfConfig):
	# get the whole list of stock names
	lName = list(dfData[0])
	lName = sorted(set(lName), key=lName.index)  # remove redundancy
	dfAlive = pd.DataFrame(columns=dfData.columns)
	for i, name in enumerate(lName):
		subData = dfData[dfData[0]==name]
		subConfig = dfConfig[dfConfig['line']==name]
		for id in list(subData[1]):
			if id in list(subConfig['indi']):
				dfAlive = pd.concat([dfAlive, subData[subData[1]==id]])
	return dfAlive


def compareSleepLevel(dfBef, dfAft, lIdxBef, lIdxAft):
	mBef = np.array(dfBef[lIdxBef])
	mAft = np.array(dfAft[lIdxAft])
	lSumBef = np.sum(mBef, axis=1)
	lSumAft = np.sum(mAft, axis=1)
	lRatio = (lSumAft - lSumBef) / lSumBef
	lName = list(dfBef[0])
	lId = list(dfAft[1])
	return lName, lId, lRatio.reshape(mBef.shape[0], 1)


def computeAccumulateRatio(dfBef, dfAft, lIdxBef, lIdxAft, divider, offset=0):
	mBef = np.array(dfBef[lIdxBef])
	mAft = np.array(dfAft[lIdxAft])
	mRatio = None
	try:
		mRatio = (mAft - mBef) / divider.reshape((mBef.shape[0],1))
	except(ValueError):
		print '\tPlease check input data dimensions: shape(mBef)=%dx%d, shape(mAft)=%dx%d' % (mBef.shape[0], mBef.shape[1], mAft.shape[0], mAft.shape[1])
	mAccRatio = np.zeros(mRatio.shape) + offset
	for c in range(mRatio.shape[1]):
		mAccRatio[:,c] += np.sum(mRatio[:,:(c+1)],axis=1)
	lName = list(dfBef[0])
	lId = list(dfAft[1])
	return lName, lId, mAccRatio


def saveData(f, headline, lName, lId, mData):
	h = open(f, 'w')
	
	
	for t, term in enumerate(headline):
		if t < len(headline) - 1:
			h.write('%s\t' % term)
		else:
			h.write('%s\n' % term)
	for i, name in enumerate(lName):
		h.write('%s\t%d\t' % (name, lId[i]))
		for j, val in enumerate(mData[i]):
			if j < len(mData[i]) - 1:
				h.write('%.3f\t' % val)
			else:
				h.write('%.3f\n' % val)
	h.close()


def writeCurve(h, l):
	for j, val in enumerate(l):
		if j < len(l) - 1:
			h.write('%.3f\t' % val)
		else:
			h.write('%.3f\n' % val)


def saveCurve(f, headline, lName, mData):
	h = open(f, 'w')
	for t, term in enumerate(headline):
		if t < len(headline) - 1:
			h.write('%s\t' % term)
		else:
			h.write('%s\n' % term)
	currName = lName[0]
	prevName = ''
	iCurrStart = 0
	iCurrStop = 0
	for i, name in enumerate(lName):
		if not name == currName:
			prevName = currName
			currName = name
			iCurrStop = i
			subM = mData[iCurrStart:iCurrStop]
			avg = np.mean(subM, axis=0)
			sem = np.std(subM, axis=0) / np.sqrt(iCurrStop-iCurrStart)
			iCurrStart = i
			h.write('%s\tavg\t' % prevName)
			writeCurve(h, avg)
			h.write('%s\tsem\t' % prevName)
			writeCurve(h, sem)
	h.close()


def reshapeData(fIn, fOutPrefix):
	df = pd.read_table(fIn)
	df.fillna(0)
	lName = list(df['name'])
	lName = sorted(set(lName), key=lName.index)
	lTerms = df.columns[2:]
	for term in lTerms:  # separately save different properties into distinct output files
		fSubOut = fOutPrefix + term + '.txt'
		h = open(fSubOut, 'w')
		h.write('%s\t' % term)
		llVal = []
		for name in lName:
			h.write('%s\t' % name)
			llVal.append(list(df[df['name']==name][term]))
		h.write('\n')
		lN = np.array([len(lVal) for lVal in llVal])  # list of number for each group
		for iRow in range(np.max(lN)):
			h.write('\t')
			for iList, lVal in enumerate(llVal):
				if iRow < lN[iList]:
					h.write('%.3f\t' % lVal[iRow])
				else:
					h.write('\t')
			h.write('\n')
		# write statistics
		for name in lName:
			h.write('\t%s' % name)
		h.write('\n')
		h.write('mean\t')
		for lVal in llVal:
			h.write('%.3f\t' % np.mean(np.array(lVal)))
		h.write('\n')
		h.write('sem\t')
		lSqrtN = np.sqrt(lN)
		for i, lVal in enumerate(llVal):
			h.write('%f\t' % (np.std(np.array(lVal)) / lSqrtN[i]))
		h.write('\n')
		h.write('N\t')
		for n in lN:
			h.write('%d\t' % n)
		h.write('\n')
		h.close()


def reshapeOneFile(fInput):
	fOutPrefix = fInput[:-4] + '-'
	reshapeData(fInput, fOutPrefix)


def saveAccumulateCurve(rootdir_bef, rootdir_aft, rangeBef, rangeAft, lRgBef, offsetBef):
	# relative paths
	fBef = os.path.join(rootdir_bef, 'SD/sleep_30mins_CT.txt')
	fAft = os.path.join(rootdir_aft, 'SD/sleep_30mins_CT.txt')
	fFltrBef = os.path.join(rootdir_bef, 'SD/sleep_30mins_CT_filtered-before.txt')
	fFltrAft = os.path.join(rootdir_aft, 'SD/sleep_30mins_CT_filtered-after.txt')
	fConfigBef = os.path.join(rootdir_bef, 'config_flys.txt')
	fConfigAft = os.path.join(rootdir_aft, 'config_flys.txt')
	fDiffRatio = os.path.join(rootdir_aft, 'SD/sleep_30mins_CT_night-change-sleep_level_different_ratio-raw.txt')
	fAccRatio = os.path.join(rootdir_aft, 'SD/sleep_30mins_CT_night-change-acc_ratio-raw.txt')
	fAccCurve = os.path.join(rootdir_aft, 'SD/sleep_30mins_CT_night-change-acc_ratio-mean_sem.txt')
	dfFltrBef, dfFltrAft = readSleepCurvePair(fBef, fAft)
	dfConfigBef = readAliveFlyList(fConfigBef, rangeBef)
	dfConfigAft = readAliveFlyList(fConfigAft, rangeAft)
	dfAliveBef = getAliveDataset(dfFltrBef, dfConfigBef)
	dfAliveBef = getAliveDataset(dfAliveBef, dfConfigAft)
	dfAliveAft = getAliveDataset(dfFltrAft, dfConfigAft)
	dfAliveAft = getAliveDataset(dfAliveAft, dfConfigBef)
	dfAliveBef.to_csv(fFltrBef, sep='\t', index=False)
	dfAliveAft.to_csv(fFltrAft, sep='\t', index=False, header=False)
	colBef = dfAliveBef.columns
	colAft = dfAliveAft.columns
	# the 1st phase ratio
	lIdxBef = colBef[(2+offsetBef+1+lRgBef[0]*24):(2+offsetBef+1+lRgBef[1]*24)]
	if len(lIdxBef) < 24:
		lIdxBef = colBef[(2+offsetBef+lRgBef[0]*24):(2+offsetBef+lRgBef[1]*24)]
	lIdxAft = colAft[(2+0):(2+24)]
	lNightBef = np.sum(np.array(dfAliveBef[np.array(lIdxBef)-24]),axis=1)
	lName, lId, mDiffRatio1st = compareSleepLevel(dfAliveBef, dfAliveAft, lIdxBef, lIdxAft)
	lName, lId, mAccRatio1st = computeAccumulateRatio(dfAliveBef, dfAliveAft, lIdxBef, lIdxAft, lNightBef)
	# the 2nd phase ratio
	lOffset = mAccRatio1st[:,-1].reshape(mAccRatio1st.shape[0], 1)
	lIdxBef = colBef[(2+offsetBef+1+(lRgBef[0]-1)*24):(2+offsetBef+1+lRgBef[0]*24)]
	lIdxAft = colAft[(2+24):(2+48)]
	lName, lId, mDiffRatio2nd = compareSleepLevel(dfAliveBef, dfAliveAft, lIdxBef, lIdxAft)
	lName, lId, mAccRatio2nd = computeAccumulateRatio(dfAliveBef, dfAliveAft, lIdxBef, lIdxAft, lNightBef, offset=lOffset)
	# save output
	mDiffRatio = np.concatenate([mDiffRatio1st, mDiffRatio2nd], axis=1)
	mAccRatio = np.concatenate([mAccRatio1st, mAccRatio2nd], axis=1)
	headline = ['name', 'id', 'stage-1 sleep change ratio', 'stage-2 sleep change ratio']
	saveData(fDiffRatio, headline, lName, lId, mDiffRatio)
	reshapeOneFile(fDiffRatio)
	headline = ['name', 'id']
	for i in np.arange(0,48)*0.5:
		headline.append(str(i))
	saveData(fAccRatio, headline, lName, lId, mAccRatio)
	saveCurve(fAccCurve, headline, lName, mAccRatio)


def run():
	# input parameters
	rootdir_bef = 'F:/20180713_SD/matlab/before-2'
	rootdir_aft = 'F:/20180713_SD/matlab/after-1'
	#rootdir_bef = 'E:/matlab_data/yw-20180508-SISLm-before'
	#rootdir_aft = 'E:/matlab_data/yw-20180508-SISLm-stv'
	rangeBef = '9,10,'  # selected phase list, use format same as in 'config_flys.txt'
	rangeAft = '1,2,'
	lRgBef = [9,10]
	offsetBef = 0  # the first phase of group-'before' data, and 2 means 30'x2
	saveAccumulateCurve(rootdir_bef, rootdir_aft, rangeBef, rangeAft, lRgBef, offsetBef)
	# the order of 2 phases in rangeBef will be inverted


run()
#test()