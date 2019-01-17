import os
import cv2 as cv
import numpy as np
import pandas as pd
import copy
import shutil


def cmpRaster(f1, f2):
	i1 = int(f1.split('--')[0])
	i2 = int(f2.split('--')[0])
	if i1 > i2:
		return 1
	elif i1 < i2:
		return -1
	else:
		return 0


def onMouse(event, x, y, flags, param):
	mode, iFly, lX, dynX = param
	dynX[0] = x
	if event == cv.EVENT_LBUTTONDOWN:
		if mode[0] == 'alive':
			lX[iFly[0]] = x
		elif mode[0] == 'total-death':
			lX[iFly[0]] = -1
	elif event == cv.EVENT_RBUTTONDOWN:
		lX[iFly[0]] = -1
	iFly[0] = max(0, int(np.floor(y / 60)))
	if iFly[0] >= len(lX):
		iFly[0] = len(lX) - 1


def loadData(rootpath):
	# load raster files
	lfRaster = []
	lFiles = os.listdir(rootpath)
	lJpg = []
	lLines = []
	for f in lFiles:
		if 'jpeg' == f.split('.')[-1]:
			lJpg.append(f)
			lLines.append(f.split('.')[0] + ':')
			lfRaster.append(f)
	# lfRaster.sort(cmpRaster)
	# load config_flys.txt
	lnFly = []
	lnPhase = []
	pathConfig = os.path.join(rootpath, 'config_flys.txt')
	dfConfig = pd.read_table(pathConfig, sep='\t')
	for stk in lLines:
		subdf = dfConfig[dfConfig['line'] == stk]
		nFly = len(list(subdf['frag']))
		lPhases = str(list(subdf['frag'])[0]).rstrip('\r\n,').split(',')
		nPhase = len(lPhases)
		lnFly.append(nFly)
		lnPhase.append(nPhase)
	return lfRaster, lnFly, lnPhase


def showDeathTime(img, idx, lX):
	if lX[idx] == 0:
		cv.line(img, (0, int(60 * (idx + 0.5))), (len(img[0]), int(60 * (idx + 0.5))), (0,0,255,0.5), 30)
	elif lX[idx] > 0:
		cv.line(img, (0, int(60 * (idx + 0.5))), (int(lX[idx]), int(60 * (idx + 0.5))), (0,0,255,0.5), 4)
		cv.line(img, (int(lX[idx]), int(60 * idx)), (int(lX[idx]), int(60 * (idx + 1))), (0,0,255), 10)


def configDeath(fImg, nFly, nPhase, offset):
	# prepare opencv GUI
	cv.namedWindow(fImg, cv.WINDOW_NORMAL)
	wImg = fImg
	mode = ['alive']
	lX = np.zeros(nFly+1) - 1  # list of x coordinates
	dynX = [-1]
	iFly = [0]
	cv.setMouseCallback(wImg, onMouse, param=(mode, iFly, lX, dynX))
	# GUI interative loop
	imgRaster = cv.imread(fImg)
	isShowHint = True
	isShowAll = True
	while(1):
		# refresh image display
		imgTmp = imgRaster.copy()
		if isShowHint:
			cv.putText(imgTmp, 'status-%s, iFly-%d, <space>=show all, h=hide hint' % (mode[0], iFly[0]+1), (30, len(imgTmp) - 15), cv.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 2)
		# refresh pointer
		cv.line(imgTmp, (0, int(60 * (iFly[0] + 0.5))), (dynX[0], int(60 * (iFly[0] + 0.5))), (0,255,0), 4)
		cv.line(imgTmp, (dynX[0], 0), (dynX[0], len(imgTmp) - 1), (0,255,0), 4)
		if lX[iFly[0]] == 0:
			cv.line(imgTmp, (0, int(60 * (iFly[0] + 0.5))), (dynX[0], int(60 * (iFly[0] + 0.5))), (0,0,255,0.5), 30)
		elif lX[iFly[0]] > 0:
			cv.line(imgTmp, (int(lX[iFly[0]]), 0), (int(lX[iFly[0]]), len(imgTmp) - 1), (0,0,255), 4)
		# show all deathtime on map
		if isShowAll:
			for idx in range(nFly):
				showDeathTime(imgTmp, idx, lX)
		cv.imshow(wImg, imgTmp)
		# check keyboard cmd
		key = cv.waitKey(1)
		if not lX[iFly[0]] == 0:
			mode[0] = 'alive'
		if key == 27:
			break
		elif key == ord('a'):
			mode[0] = 'alive'
			lX[iFly[0]] = -1
		elif key == ord('s'):
			mode[0] = 'total-death'
			lX[iFly[0]] = 0
		elif key == ord('d'):
			iFly[0] -= 1
			if iFly[0] < 0:
				iFly[0] = 0
		elif key == ord('f'):
			iFly[0] += 1
			if iFly[0] >= nFly + 1:
				iFly[0] = nFly
		elif key == ord('h'):
			isShowHint = 1 - isShowHint
		elif key == ord(' '):
			isShowAll = 1 - isShowAll
	lDeathTime = lX
	lDeathPhase = []
	for t in lX:
		if t == -1:
			lDeathPhase.append(str(nPhase))
		elif t == 0:
			lDeathPhase.append('none')
		elif t > 0 and t < offset:
			lDeathPhase.append('none')
		elif offset == 0 and (t-offset) / 720 < 1 and (t-offset) / 720 >= 0:
			lDeathPhase.append('none')
		else:
			if offset > 0:
				lDeathPhase.append(str(int((t-offset) / 720) + 1))
			else:
				lDeathPhase.append(str(int((t-offset) / 720)))
	cv.destroyWindow(wImg)
	return lDeathTime, lDeathPhase


def saveData(rootpath, fImg, lDeathTime, lDeathPhase):
	# save precise death time
	pathDeathTime = os.path.join(rootpath, 'deathtime.txt')
	hDt = None
	if not os.path.exists(pathDeathTime):
		hDt = open(pathDeathTime, 'w')
	else:
		hDt = open(pathDeathTime, 'a')
	hDt.write('%s\t' % fImg.rstrip('.jpeg'))
	for dt in lDeathTime[:-1]:
		hDt.write('%d\t' % int(dt))
	hDt.write('\n')
	hDt.close()
	# save death phase info
	pathDeathPhase = os.path.join(rootpath, 'config_flys-corrected.txt')
	hDp = None
	if not os.path.exists(pathDeathPhase):
		hDp = open(pathDeathPhase, 'w')
		hDp.write('line\tindi\tfrag\n')
	else:
		hDp = open(pathDeathPhase, 'a')
	for iF, dp in enumerate(lDeathPhase[:-1]):
		hDp.write('%s:\t%d\t' % (fImg.rstrip('.jpeg'), iF+1))
		if dp == 'none':
			hDp.write(dp)
		else:
			for i in range(int(dp)):
				hDp.write('%d,' % (i + 1))
		hDp.write('\n')
	hDp.close()


def runtask(rootpath):
	# [input] load raster maps
	lfRaster, lnFly, lnPhase = loadData(rootpath)
	offset = int(raw_input('offset='))
	# [loop] configure and save survival data
	for i, fImg in enumerate(lfRaster):
		# [config] interactively label survival time
		lDeathTime, lDeathPhase = configDeath(fImg, lnFly[i], lnPhase[i], offset)
		saveData(rootpath, fImg, lDeathTime, lDeathPhase)
		print '[Saved]: Channel [%s]\n\tnFly = %d, nPhase = %d.\n' % (fImg, lnFly[i], lnPhase[i])
	# rename saved death configuration file
	pathCurr = os.path.join(rootpath, 'config_flys-corrected.txt')
	pathOri = os.path.join(rootpath, 'config_flys-ori.txt')
	pathValid = os.path.join(rootpath, 'config_flys.txt')
	shutil.move(pathValid, pathOri)
	shutil.copy(pathCurr, pathValid)


def test():
	pass

def runConfigDeath(workdir):
	rootpath = os.path.join(workdir, workdir.split('\\')[-1])
	runtask(rootpath)
	#test()
	return True

#runConfigDeath('.')