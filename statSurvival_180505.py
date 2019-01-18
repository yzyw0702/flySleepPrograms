import os
import cv2 as cv
import numpy as np
import copy


class Stock:
	def __init__(self, name):
		self.name = name
		self.lChnRoi = []
		self.mData = []
		self.avg = 0.0
		self.sem = 0.0
	def __str__(self):
		return "%s, nChn = %d" % (self.name, size(self.lChn))


def cmpChk(f1, f2):
	i1 = int(f1.split('-')[3].split('_')[0])
	i2 = int(f2.split('-')[3].split('_')[0])
	if i1 > i2:
		return 1
	elif i1 < i2:
		return -1
	else:
		return 0


def isInList(query, lPts):
	for i, pt in enumerate(lPts):
		if np.sqrt((query[0] - pt[0])**2 + (query[1] - pt[1])**2) < 10:
			return i
	return -1


def onMouse(event, x, y, flags, param):
	mode, llPts, iImg, lNum = param
	if event == cv.EVENT_LBUTTONDOWN:
		iPt = isInList((float(x), float(y)), llPts[iImg[0]])
		if mode[0] == 'add':
			if iPt == -1:
				llPts[iImg[0]].append((x, y))
				# refresh number list
				if iImg[0] < len(lNum) - 1:
					for i in range(iImg[0]+1, len(llPts)):
						if len(llPts[iImg[0]]) > len(llPts[i]):
							llPts[i] = copy.deepcopy(llPts[iImg[0]])
						else:
							llPts[i].insert(len(llPts[iImg[0]])-1, (x, y))
						lNum[i] += 1
		elif mode[0] == 'remove':
			elem = None
			if iPt > -1:
				elem = llPts[iImg[0]][iPt]
				del(llPts[iImg[0]][iPt])
				# refresh number list
				if iImg[0] < len(lNum) - 1:
					for i in range(iImg[0]+1, len(llPts)):
						llPts[i].remove(elem)
						lNum[i] -= 1
	elif event == cv.EVENT_RBUTTONDOWN:
		iPt = isInList((float(x), float(y)), llPts[iImg[0]])
		elem = llPts[iImg[0]][iPt]
		del(llPts[iImg[0]][iPt])
		# refresh number list
		if iImg[0] < len(lNum) - 1:
			for i in range(iImg[0]+1, len(llPts)):
				llPts[i].remove(elem)
				lNum[i] -= 1


def loadConfig(fConfig):
	dStocks = {}
	hConfig = open(fConfig, 'r')
	lLines = [line.rstrip('\r\n\t') for line in hConfig.readlines()]
	hConfig.close()
	# get channel configuration
	for line in lLines:
		if 'ch-' in line:
			lTerms = line.split('\t')
			iChn = int(lTerms[0].split('-')[1])
			lPlates = lTerms[1].split(', ')
			for iPlt, plt in enumerate(lPlates):
				if len(dStocks.keys()) == 0 or (iChn, iPlt) not in dStocks.keys():
					stk = Stock(plt)
					dStocks[(iChn, iPlt)] = stk
				dStocks[(iChn, iPlt)].lChnRoi.append((iChn, iPlt))
	return dStocks


def loadData(rootpath):
	lfTtlmean = []
	llfMaps = []
	# get all .png files
	lFiles = os.listdir(rootpath)
	lPngs = []
	for f in lFiles:
		if 'png' in f:
			lPngs.append(f)
	#print 'Load %d pngs.' % len(lPngs)
	# sort photos according to their usage and group
	lChns = []
	for f in lPngs:
		if 'total-meanframe' in f:
			lfTtlmean.append(os.path.join(rootpath, f))
		elif 'label-map' in f:
			chn = f.split('_')[0]
			if chn not in lChns:
				lChns.append(chn)
				llfMaps.append([])
			llfMaps[-1].append(f)
	for i, chn in enumerate(lChns):
		llfMaps[i].sort(cmpChk)
	return lfTtlmean, llfMaps


def loadRoi(rootpath, fRoi):
	hRoi = open(os.path.join(rootpath, fRoi), 'r')
	lLines = [line.rstrip('\r\t\n') for line in hRoi.readlines()]
	hRoi.close()
	iCh = -1
	iRoi = -1
	dRoi = {}
	for line in lLines:
		if 'Roi' in line:
			lRnk0 = line.split('\t')
			lRnk00 = lRnk0[0].split('.')
			iCh = int(lRnk00[0].split('-')[1])
			iRoi = int(lRnk00[1].split('-')[1])
			x, y, w, h = [int(term) for term in lRnk0[1].split(', ')]
			dRoi[(iCh, iRoi)] = (x, y, w, h)
	return dRoi


def countNum(iChn, lImg, roi):
	# prepare opencv GUI
	wImg = 'Channel-' + str(iChn)
	cv.namedWindow(wImg)
	mode = ['add']
	lNum = np.zeros(len(lImg))
	llPts = []
	for i in range(len(lNum)):
		llPts.append([])
	iImg = [0]
	isDrawing = False
	cv.setMouseCallback(wImg, onMouse, param=(mode, llPts, iImg, lNum))
	# GUI interative loop
	imgTmp = None
	while(1):
		# refresh image display
		imgTmp = lImg[iImg[0]].copy()
		cv.circle(imgTmp, (roi[0] + roi[2] / 2, roi[1] + roi[3] / 2), (roi[2] + roi[3])/4, (0, 0, 255), 2)
		cv.putText(imgTmp, 'mode-%s, chk-%d' % (mode[0], iImg[0]+1), (30, len(lImg[0]) - 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
		for i, pt in enumerate(llPts[iImg[0]]):
			cv.circle(imgTmp, pt, 8, (255,255,0))
			cv.putText(imgTmp, '%d' % i, (pt[0]+8, pt[1]+8), cv.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,0))
		cv.imshow(wImg, imgTmp)
		# check keyboard cmd
		key = cv.waitKey(1)
		if key == 27:
			break
		elif key == ord('a'):
			mode[0] = 'add'
		elif key == ord('s'):
			mode[0] = 'remove'
		elif key == ord('d'):
			iImg[0] -= 1
			if iImg[0] < 0:
				iImg[0] = 0
		elif key == ord('f'):
			iImg[0] += 1
			if iImg[0] >= len(lImg):
				iImg[0] = len(lImg) - 1
		
	return lNum


def runtask(rootpath):
	fConfig = os.path.join(rootpath, 'configure.txt')
	dStocks = loadConfig(fConfig)
	lfTtlmean, llfMaps = loadData(rootpath)
	dRois = loadRoi(rootpath, 'trace-output.txt')
	dNum = {}
	# test with one image series
	fOutput = os.path.join(rootpath, os.getcwd().split('\\')[-1].rstrip('/\\') + '-count-output.txt')
	while os.path.exists(fOutput):
		fOutput = fOutput + '-1.txt'
	hOutput = open(fOutput, 'w')
	hOutput.write('idx-channel\tidx-roi\tgroup-name\tidx-checkpoint\tdeath-count\tsurvival\n')
	for lfMaps in llfMaps:  # for each channel
		lImgSeries = []
		for fImg in lfMaps:  # create image series
			lImgSeries.append(cv.imread(fImg, 1))
		iFChn = int(lfMaps[0].split('_')[0].split('-')[1])
		for idxChnRoi in dRois.keys():
			iCh, iRoi = idxChnRoi
			if iCh == iFChn:
				roi = dRois[idxChnRoi]
				dNum[idxChnRoi] = countNum(iCh, lImgSeries, roi)
				for t, num in enumerate(dNum[idxChnRoi]):
					if dNum[idxChnRoi][-1] == 0:
						hOutput.write('%d\t%d\t%s\t%d\t%d\t%f\n' % (iCh, iRoi,dStocks[idxChnRoi].name, (t+1) * 2, num, -1))
					else:
						hOutput.write('%d\t%d\t%s\t%d\t%d\t%f\n' % (iCh, iRoi,dStocks[idxChnRoi].name, (t+1) * 2, num, float((dNum[idxChnRoi][-1] - num)) / dNum[idxChnRoi][-1]))
	hOutput.close()


def test():
	pass

def main():
	rootpath = '.'
	runtask(rootpath)
	#test()
	return 0


if __name__ == '__main__':
	main()