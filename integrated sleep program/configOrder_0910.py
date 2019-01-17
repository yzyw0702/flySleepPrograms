import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as py
import os
import thread


def showOrder(wImg, fImg):
	mOrder = mpimg.imread(fImg)
	plt.imshow(mOrder)
	plt.title(wImg)
	try:
		plt.show()
		plt.close()
	except(_tkinter.TclError):
		print '',


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
	while(1):
		isValid = True
		line = raw_input('%s [nRoi = %d] --- input <stock,number; ...>: ' % (wSrc, nRoi))
		for p in line.split(';'):
			if len(p) == 0:
				break
			nFly = 0
			try:
				lTerms = p.split(',')
				stk = lTerms[0]
				nFly = int(lTerms[1])
				hOutput.write(stk + ':\t')
			except(IndexError):
				isValid = False
				print '\tinvalid setting, try again.'
				break
			for i in range(nFly):
				if i < nFly - 1:
					hOutput.write('%d,' % i)
				else:
					hOutput.write('%d' % i)
			hOutput.write('\n')
		if isValid:
			hOutput.close()
			break


def configOrder(workdir):
	for dir in os.listdir(workdir):
		pathdir = os.path.join(workdir,dir)
		if os.path.isdir(pathdir):
			if 'order.png' in os.listdir(pathdir):
				if 'txt.order' in os.listdir(pathdir):
					continue
				nRoi = countRoi(os.path.join(pathdir, 'config.yaml'))
				#thread.start_new_thread(showOrder,(dir, os.path.join(pathdir, 'order.png'),))
				saveOrder(os.path.join(pathdir, 'txt.order'), pathdir, nRoi)
	return True
