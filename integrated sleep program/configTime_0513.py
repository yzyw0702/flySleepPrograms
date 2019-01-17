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
	fOutput = os.path.join(workdir, 'config_time.txt')
	if os.path.exists(fOutput):
		print 'time configuration already saved.'
		return True
	offset = int(raw_input('\toffset (unit: min) = '))
	initStat = int(raw_input('\tinitial status (0=dark, 1=light) = '))
	for dir in os.listdir(workdir):
		if dir == '..' or dir == '.':
			continue
		pathdir = os.path.join(workdir, dir)
		if os.path.isdir(pathdir):
			nAvi = countAvi(pathdir)
			if nAvi > 0:
				saveTimeSeries(fOutput, nAvi, offset, initStat)
				break
	return True
	
configTime('.')