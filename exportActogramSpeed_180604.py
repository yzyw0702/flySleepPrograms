import os
import numpy as np


def loadSpeed(fSpd, offset = 0):
	print 'Loading: ' + fSpd,
	mSpd = []
	with open(fSpd, 'r') as hSpd:
		for i,line in enumerate(hSpd):
			line = line.rstrip('\r\n')
			if i < offset:
				continue
			lSpd = []
			try:
				lSpd = [float(val) for val in line.split('\t')[:-1]]
			except(ValueError):
				print line.split('\t')
			mSpd.append(lSpd)
			lSpd = []
		hSpd.close()
	print '. Done.'
	return np.array(mSpd)


def writeActogramSpeed(fOutput, mSpd, interval=60):
	print 'Saving: ' + fOutput,
	nSec, nFly = mSpd.shape
	nTime = nSec / interval  # omit the last min if < interval
	hOutput = open(fOutput,'w')
	for i in range(nTime):
		lAct = mSpd[(i * interval):((i+1) * interval)].sum(axis=0)
		for j,act in enumerate(lAct):
			if j < len(lAct) - 1:
				hOutput.write('%f\t' % act)
			else:
				hOutput.write('%f' % act)
		hOutput.write('\n')
		lAct = []
	hOutput.close()
	print '. Done.'


def batch(rootpath):
	offset = 3600
	interval = 60
	for d in os.listdir(rootpath):
		pathdir = os.path.join(rootpath, d)
		if not os.path.isdir(pathdir):
			continue
		if 'txt.speed' in os.listdir(pathdir):
			while(1):
				fInput = os.path.join(pathdir, 'txt.speed')
				fConfig = os.path.join(pathdir, 'txt.order')
				hConfig = open(fConfig, 'r')
				stock = hConfig.readline().split('\t')[0][:-1]
				hConfig.close()
				fOutput = 'actogram-ch%s-%s-offset%d.txt' % (d, stock, offset)
				fOutput = os.path.join(rootpath, fOutput)
				try:
					mSpd = loadSpeed(fInput, offset)
				except(MemoryError):
					mSpd = []
					continue
				writeActogramSpeed(fOutput, mSpd, interval)
				mSpd = []
				break



def test():
	fSpd = 'C:/Users/pc/Documents/testActogramJ/txt-M1KOm.speed'
	offset = 3600
	interval = 60
	fOutput = '%s-offset%d-actogram.txt' % (fSpd, offset)
	mSpd = loadSpeed(fSpd, offset)
	writeActogramSpeed(fOutput, mSpd, interval)


batch('.')