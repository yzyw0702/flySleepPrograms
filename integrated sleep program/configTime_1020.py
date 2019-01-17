import os
import time
import math

def clkMinLen(fTm):
	ascTm = fTm.rstrip('.avi')[fTm.find('-')+1:]
	lTerms = ascTm.split('-')
	date = lTerms[0] + '-' + lTerms[1] + '-' + lTerms[2]
	stmStart = date + '-' + lTerms[3]
	stmStop = date + '-' + lTerms[4]
	tmStart = time.strptime(stmStart, '%Y-%m-%d-%H.%M.%S')
	tmStop = time.strptime(stmStop, '%Y-%m-%d-%H.%M.%S')
	if tmStop.tm_hour == 0:
		secStop = time.mktime(tmStop) + 24 * 60 * 60
		tmStop = time.localtime(secStop)
	return (time.mktime(tmStop) - time.mktime(tmStart)) / 60


def countMin(rootpath):
	# list all avi files
	nMin = 0
	pathfTm = os.path.join(rootpath, 'list.txt')
	if not os.path.exists(pathfTm):
		return nMin
	hTm = open(pathfTm, 'r')
	lfTm = [line.rstrip('\r\n') for line in hTm.readlines()]
	hTm.close()
	for fTm in lfTm:
		nMin += clkMinLen(fTm)
	return nMin


def saveTimeSeries(fOutput, nMin, offset, initStat):
	hOutput = open(fOutput, 'w')
	tCurr = 0
	stCurr = initStat
	for i in range(int(math.ceil(nMin / (12*60)))):
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
	if tCurr < nMin:
		hOutput.write('%d\t%d\t%d\n' % (tCurr+1, nMin-1, stCurr))
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
			nMin = countMin(pathdir)
			if nMin > 0:
				saveTimeSeries(fOutput, nMin, offset, initStat)
				break
	return True
	
#configTime('.')