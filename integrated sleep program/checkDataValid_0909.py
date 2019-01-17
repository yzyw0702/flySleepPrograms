import os


def lenFile(f):
	nL = 0
	nC = 0
	nFly = 0
	hasBug = False
	isBugInPrevLine = False
	lBugLine = []
	h = open(f, 'r')
	for l in h.readlines():
		nL+=1
		nC = len(l.rstrip('\t\r\n').split('\t'))
		if nL == 1:
			nFly = nC
		elif isBugInPrevLine:
			nFly = nC
			isBugInPrevLine = False
		elif not nC == nFly:
			lBugLine.append(nL)
		if '-1.#QNAN' in l:
			hasBug = True
			isBugInPrevLine = True
	h.close()
	return nL, nC, hasBug, lBugLine


def lenFlyList(f):
	n = 0
	h = open(f, 'r')
	for l in h.readlines():
		n += len(l.rstrip('\t\r\n').split('\t')[1].split(','))
	return n


def lenSetTime(f):
	len = 0
	h = open(f, 'r')
	for l in h.readlines():
		len = int(l.rstrip('\r\n').split('\t')[1])
	return len * 60


def rmBugLine(fErr):
	# collect info about locations of bug lines
	hErr = open(fErr, 'r')
	dlErr = {}
	key = None
	isRecord = False
	for line in hErr.readlines():
		if 'contains abnormal characters' in line:
			key = line.rstrip('\r\n').split(' ')[0]
			isRecord = True
			continue
		if isRecord:
			dlErr[key] = [int(v)-1 for v in line.rstrip(', \r\n').lstrip('\t').split(', ')]
			isRecord = False
	hErr.close()
	# remove bug lines and overwrite bug files
	hErr = open(fErr, 'a')
	for f in dlErr.keys():
		print 'remove bug lines at file ' + f
		lLines = []
		with open(f, 'r') as h:
			for i, line in enumerate(h.readlines()):
				if i in dlErr[f]:
					continue
				lLines.append(line)
		with open(f, 'w') as h:
			h.writelines(lLines)
		del lLines
		hErr.write('bug lines at file %s have been removed.\n' % f)
	hErr.close()


def batchCount(rootpath):
	# check config_time.txt
	pathTime = os.path.join(rootpath, 'config_time.txt')
	lenConfigTime = lenSetTime(pathTime)
	# set output files
	fOut = os.path.join(rootpath, 'infoFlyData.txt')
	fErr = os.path.join(rootpath, 'errorFlyData.txt')
	hOut = open(fOut, 'w')
	hErr = open(fErr, 'w')
	hOut.write('# script verion = 0909\n')
	hOut.write('file\tlen-txt.speed\tlen-txt.location\tlen-orderlist\n')
	# hOut.write('file\tlen-orderlist\n')
	# check every channel subdirectory
	hasBugLines = False
	for dir in os.listdir(rootpath):
		pathd = os.path.join(rootpath, dir)
		if os.path.isdir(pathd):
			print 'check directory [%s]' % pathd
			pathSpd = os.path.join(pathd, 'txt.speed')
			pathLoc = os.path.join(pathd, 'txt.location')
			pathOdr = os.path.join(pathd, 'txt.order')
			isMissing = False
			lenSpd = nFlySpd = lenLoc = nFlyLoc = lenOdr = 0
			if not os.path.exists(pathSpd):
				msg = '%s/txt.speed is missing.' % pathd
				hErr.write(msg+'\n')
				print msg
				isMissing = True
			if not os.path.exists(pathLoc):
				msg = '%s/txt.location is missing.' % pathd
				hErr.write(msg+'\n')
				print msg
				isMissing = True
			if not os.path.exists(pathOdr):
				msg = '%s/txt.order is missing.' % pathd
				hErr.write(msg+'\n')
				print msg
				isMissing = True
			if isMissing:
				hOut.write('%s\t%dx%d\t%dx%d\t%d\n' % (pathd, lenSpd, nFlySpd, lenLoc, nFlyLoc, lenOdr))
				continue
			lenSpd, nFlySpd, hasBugInSpd, lBugLineSpd = lenFile(pathSpd)
			lenLoc, nFlyLoc, hasBugInLoc, lBugLineLoc = lenFile(pathLoc)
			lenOdr = lenFlyList(pathOdr)
			if lenSpd < lenConfigTime:
				msg = '%s/txt.speed end-time is shorter than that in config_time.txt.' % pathd
				hErr.write(msg+'\n')
				print msg
			if lenLoc < lenConfigTime:
				msg = '%s/txt.location end-time is shorter than that in config_time.txt.' % pathd
				hErr.write(msg+'\n')
				print msg
			if len(lBugLineSpd) > 0:
				hasBugLines = True
				msg = '%s/txt.speed contains abnormal characters at lines #:\n' % pathd
				msg += '\t'
				for s in lBugLineSpd:
					msg += str(s) + ', '
				hErr.write(msg + '\n')
				print msg
			if len(lBugLineLoc) > 0:
				hasBugLines = True
				msg = '%s/txt.location contains abnormal characters at lines #:\n' % pathd
				msg += '\t'
				for s in lBugLineLoc:
					msg += str(s) + ', '
				hErr.write(msg + '\n')
				print msg
			if hasBugInSpd:
				msg = '%s/txt.speed has bug-code "-1.#QNAN" ' % pathd
				hErr.write(msg+'\n')
				print msg
			if hasBugInLoc:
				msg = '%s/txt.location has bug-code "-1.#QNAN" ' % pathd
				hErr.write(msg+'\n')
				print msg
			if not nFlySpd == lenOdr:
				if nFlySpd < lenOdr:
					msg = '%s/txt.speed is invalid.' % pathd
				else:
					msg = '%s/txt.order is invalid.' % pathd
				hErr.write(msg+'\n')
				print msg
			if not nFlyLoc/2 == lenOdr:
				print '%s/txt.location is invalid.' % pathd
			hOut.write('%s\t%dx%d\t%dx%d\t%d\n' % (pathd, lenSpd, nFlySpd, lenLoc, nFlyLoc, lenOdr))
			#hOut.write('%s\t%d\n' % (pathd, lenOdr))
	hOut.write('config_time total time length = %d sec\n' % lenConfigTime)
	hOut.close()
	hErr.close()
	
	if hasBugLines: # if files contain shorter line, remove them
		print 'start removing bug lines.'
		rmBugLine(fErr)
	


batchCount('.')