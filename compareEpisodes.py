import numpy as np
import pandas as pd
import os


def readCleanBoutDataPair(fBef, fAft):
	dfBef = pd.read_table(fBef)
	dfAft = pd.read_table(fAft)
	dfBef.fillna(0)
	dfAft.fillna(0)
	lName = list(dfBef['name'])
	lName = sorted(set(lName), key=lName.index)
	dfFltrBef = pd.DataFrame(columns=dfBef.columns)
	dfFltrAft = pd.DataFrame(columns=dfAft.columns)
	for i, name in enumerate(lName):
		subBef = dfBef[dfBef['name']==name]
		subAft = dfAft[dfAft['name']==name]
		for id in list(subBef['id']):
			if id in list(subAft['id']):
				dfFltrBef = pd.concat([dfFltrBef, subBef[subBef['id']==id]])
				dfFltrAft = pd.concat([dfFltrAft, subAft[subAft['id']==id]])
	return dfFltrBef, dfFltrAft


def compareVals(dfBef, dfAft, lKeys):
	mBef = np.array(dfBef[lKeys])
	mAft = np.array(dfAft[lKeys])
	mRatio = (mAft - mBef) / mBef
	lName = list(dfBef['name'])
	lId = list(dfAft['id'])
	return lName, lId, mRatio


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


def run():
	fBefore = 'E:/matlab_data/yw-20180508-SISLm-before/sleepEpisode/sleepEpisode_clean.txt'
	fAfter = 'E:/matlab_data/yw-20180508-SISLm-stv/sleepEpisode/sleepEpisode_clean.txt'
	fFltrBef = 'E:/matlab_data/yw-20180508-SISLm-before/sleepEpisode/sleepEpisode_fltrbef.txt'
	fFltrAft = 'E:/matlab_data/yw-20180508-SISLm-stv/sleepEpisode/sleepEpisode_fltraft.txt'
	fRatio = 'E:/matlab_data/yw-20180508-SISLm-stv/sleepEpisode/sleepEpisodeChangeRatio_clean.txt'
	dfFltrBef, dfFltrAft = readCleanBoutDataPair(fBefore, fAfter)
	lName, lId, mRatio = compareVals(dfFltrBef, dfFltrAft, dfFltrAft.columns[2:])
	dfFltrBef.to_csv(fFltrBef, sep='\t', index=False)
	dfFltrAft.to_csv(fFltrAft, sep='\t', index=False)
	saveData(fRatio, dfFltrAft.columns, lName, lId, mRatio)


run()