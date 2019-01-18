import os
import shutil


def gatherAll(workdir, pattern='.dav'):
	fLog = os.path.join(workdir, 'movefilelog.txt')
	hLog = open(fLog, 'w')
	print '[Task] gather all %s files to current working directory.' % pattern
	for root, dir, files in os.walk(workdir, topdown=True):
		for name in files:
			if pattern in name:
				try:
					hLog.write('%s -> %s' (os.path.join(root,name), os.path.join(workdir,name)))
					shutil.move(os.path.join(root,name), workdir)
				except(shutil.Error):
					print 'Redundant file detected: ' + name
	print '\t[Complete] All %s files have been gathered to current working directory' % pattern
	hLog.close()


def retractGatherAll(workdir):
	fLog = os.path.join(workdir, 'movefilelog.txt')
	hLog = open(fLog,'r')
	lSteps = [line.rstrip('\r\n') for line in hLog.readlines()]
	hLog.close()
	nFailed = 0
	for step in lSteps:
		dst, src = step.split(' -> ')
		try:
			shutil.move(src, dst)
		except(shutil.Error):
			nFailed += 1
			print 'warning: file retract operation %s -> %s failed.' % (src, dst)
	if nFailed == 0:
		print '\t[Retract] All gathered files have been retracted back to original paths.'
	else:
		print '\t[Failed] %d files failed to retract.' % nFailed
	os.remove(fLog)


def simulateGatherAll(workdir):
	for i in range(10):
		subdir = os.path.join(workdir, 'sub-%d' % i)
		os.mkdir(subdir)
		for j in range(5):
			ssubdir = os.path.join(subdir, 'subsub-%d' % j)
			os.mkdir(ssubdir)
			for m in range(20):
				f = os.path.join(ssubdir, 'sub-%d_ssub-%d_f-%d.txt' % (i,j,m))


gatherAll('.')