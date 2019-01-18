import matplotlib.pyplot as plt
import os


def loadLight(subdir):
	f = os.path.join(subdir, 'light_intensity.txt')
	h = open(f, 'r')
	lData = []
	for i,line in enumerate(h.readlines()):
		term = line.rstrip('\t\r\n')
		if i==0:
			continue
		lData.append(float(term))
	h.close()
	return lData


def batchLoadLight(rootpath):
	mData = []
	for sub in os.listdir(rootpath):
		subdir = os.path.join(rootpath, sub)
		if not os.path.isdir(subdir):
			continue
		if not 'light_intensity.txt' in os.listdir(subdir):
			continue
		mData.append(loadLight(subdir))
	nPlot = len(mData)
	plt.figure()
	for i in range(nPlot):
		plt.subplot(nPlot, 1, i + 1 )
		plt.plot(mData[i])
	fOut = os.path.join(rootpath, 'lightplot.png')
	plt.savefig(fOut)
	plt.show()
	


batchLoadLight('.')