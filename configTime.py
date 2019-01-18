import os


def countAvi(rootpath):
	# list all avi files
	nAvi = 0
	for f in os.listdir(rootpath):
		if '.avi' in f:
			nAvi += 1
	return nAvi


def saveTimeSeries(fOutput, nAvi, offset, initStat):
	hOutput = open(fOutput, 'w')
	tCurr = 0
	stCurr = initStat
	for i in range(nAvi / 6):
		tCurr += 1
		hOutput.write('%d\t' % tCurr)
		if i == 0 and offset > 0:
			tCurr = offset
		elif i == 0 and offset == 0:
			tCurr = 720
		else:
			tCurr += 720 - 1
		hOutput.write('%d\t%d\n' % (tCurr, stCurr))
		# set next phase status
		stCurr = 1 - stCurr
	hOutput.close()


def configTime(workdir):
	offset = int(raw_input('offset (unit: min) = '))
	initStat = int(raw_input('initial status (0=dark, 1=light) = '))
	fOutput = os.path.join(workdir, 'config_time.txt')
	for dir in os.listdir(workdir):
		if dir == '..' or dir == '.':
			continue
		if os.path.isdir(dir):
			nAvi = countAvi(dir)
			if nAvi > 0:
				saveTimeSeries(fOutput, nAvi, offset, initStat)
				break

configTime('.')