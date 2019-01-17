import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as py
import os
import thread


def showOrder(wImg, fImg):
	mOrder = mpimg.imread(fImg)
	plt.imshow(mOrder)
	plt.title(wImg)
	plt.show()
	plt.close()


def countRoi(fConfig):
	hConfig = open(fConfig, 'r')
	for line in hConfig.readlines():
		if 'count_box' in line:
			nRoi = int(line.rstrip(' \t\r\n').split(': ')[1])
			hConfig.close()
			return nRoi
	return -1


def saveOrder(fOutput, wSrc, nRoi):
	hOutput = open(fOutput, 'w')
	line = raw_input('%s [nRoi = %d] --- input <stock,number; ...>: ' % (wSrc, nRoi))
	for p in line.split(';'):
		if len(p) == 0:
			break
		lTerms = p.split(',')
		stk = lTerms[0]
		nFly = int(lTerms[1])
		hOutput.write(stk + ':\t')
		for i in range(nFly):
			if i < nFly - 1:
				hOutput.write('%d,' % i)
			else:
				hOutput.write('%d' % i)
		hOutput.write('\n')
	hOutput.close()


def configOrder(workdir):
	for dir in os.listdir(workdir):
		if os.path.isdir(dir):
			pathdir = os.path.join(workdir,dir)
			if 'order.png' in os.listdir(pathdir):
				nRoi = countRoi(os.path.join(pathdir, 'config.yaml'))
				#thread.start_new_thread(showOrder,(dir, os.path.join(pathdir, 'order.png'),))
				saveOrder(os.path.join(pathdir, 'txt.order'), pathdir, nRoi)


configOrder('.')