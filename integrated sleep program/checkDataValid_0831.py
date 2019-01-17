import os


def lenFile(f):
	nL = 0
	nC = 0
	hasBug = False
	h = open(f, 'r')
	for l in h.readlines():
		nL+=1
		if nL == 1:
			nC += len(l.rstrip('\t\r\n').split('\t'))
		if '-1.#QNAN' in l:
			hasBug = True
	h.close()
	return nL, nC, hasBug


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



def batchCount(rootpath):
	# check config_time.txt
	pathTime = os.path.join(rootpath, 'config_time.txt')
	lenConfigTime = lenSetTime(pathTime)
	# set output files
	fOut = os.path.join(rootpath, 'infoFlyData.txt')
	fErr = os.path.join(rootpath, 'errorFlyData.txt')
	hOut = open(fOut, 'w')
	hErr = open(fErr, 'w')
	hOut.write('file\tlen-txt.speed\tlen-txt.location\tlen-orderlist\n')
	# hOut.write('file\tlen-orderlist\n')
	# check every channel subdirectory
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
			lenSpd, nFlySpd, hasBugInSpd = lenFile(pathSpd)
			lenLoc, nFlyLoc, hasBugInLoc = lenFile(pathLoc)
			lenOdr = lenFlyList(pathOdr)
			if lenSpd < lenConfigTime:
				msg = '%s/txt.speed end-time is shorter than that in config_time.txt.' % pathd
				hErr.write(msg+'\n')
				print msg
			if lenLoc < lenConfigTime:
				msg = '%s/txt.speed end-time is shorter than that in config_time.txt.' % pathd
				hErr.write(msg+'\n')
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


batchCount('.')