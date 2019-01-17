# imported modules
import commands
import os
import shutil
import mlab
from mlab.releases import latest_release as matlab
from math import ceil
# DIY modules
from grouping import *
from emailHints import *
from configTime_1020 import *
from configOrder_1020 import *
from configDeath_1020 import *
import sys
sys.path.append('./MSleepSummariser_20160616')
from callGui import *

# globle parameters
lRcvProgress = ['yzyw0702@163.com']
prgCvt2Avi = '.\player\play.exe'
prgConfigRoi = 'AppSingleTracer_v4.3_x64-delay.exe'
prgTrace = 'AppSingleTracer_v4.3_x64-delay.exe'

def gatherAll(workdir, pattern='.dav'):
	print '[Task] gather all %s files to current working directory.' % pattern
	for root, dir, files in os.walk(workdir, topdown=True):
		for name in files:
			if pattern in name:
				try:
					shutil.move(os.path.join(root,name), workdir)
				except(shutil.Error):
					print 'Redundant file detected: ' + name
	print '\t[Complete] All %s files have been gathered to current working directory' % pattern


def countClips(workdir, pattern='.dav'):
	N = 0
	for f in os.listdir(workdir):
		if pattern in f:
			N += 1
	return N


def renameDav(workdir):
	print '[Task] rename all dav files'
	matlab.path(matlab.path(), r'./matlab')
	try:
		matlab.renameDav()
	except(mlab.matlabcom.MatlabError):
		print 'no file has been renamed.'
		return
	progress =  '\t[Complete] All dav files have been renamed;'
	print progress
	txt = 'workdir = %s\nprogress = %s\n' % (workdir, progress)
	emailProgress(txt, lRcvProgress)
	


def cvt2Avi(workdir):
	print '[Task] convert dav to avi'
	nDav = countClips(workdir, '.dav')
	os.system(prgCvt2Avi)
	nAvi = countClips(workdir, '.avi')
	if nDav == nAvi:
		progress = '\t[Complete] All .dav converted to .avi;'
		print progress
		txt = 'workdir = %s\nprogress = %s\n' % (workdir, progress)
		emailProgress(txt, lRcvProgress)
	else:
		progress =  '\t[Failed] %d .dav not complete;' % (nDav - nAvi)
		print progress
		txt = 'workdir = %s\nprogress = %s\n' % (workdir, progress)
		emailProgress(txt, lRcvProgress)


def startTracing(workdir):
	print '[Task] configure video tracing'
	print 'set time point for configuration operation'
	iConfigClip = int(raw_input('clip index = '))
	iConfigFr = int(raw_input('frame index = '))
	cmd = '%s --mode configure --rootpath %s --param %d %d' % (prgConfigRoi, workdir, iConfigClip, iConfigFr)
	os.system(cmd)
	# read task list
	fTask = os.path.join(workdir, 'tasklist.txt')
	hTask = open(fTask, 'r')
	lTasks = [line.rstrip('\r\n') for line in hTask.readlines()]
	hTask.close()
	fTaskTmp = fTask + '-bk'
	shutil.move(fTask, fTaskTmp)
	lBatch = []
	print 'set time point for video tracing operation'
	iStartClip = int(raw_input('start clip index = '))
	iStartFr = int(raw_input('start frame index = '))
	iStopClip = int(raw_input('stop clip index (-1 means last clip) = '))
	iStopFr = int(raw_input('stop frame index (-1 means last frame) = '))
	cmd = '%s --mode tracing --rootpath %s --param %d %d %d %d' % (prgConfigRoi, workdir, iStartClip, iStartFr, iStopClip, iStopFr)
	for i,task in enumerate(lTasks):
		lBatch.append(task)
		if (i+1) % 16 == 0 or (i + 1) == len(lTasks):
			nCurrBatch = min(16, len(lTasks))
			progress = 'workdir = %s\nstart tracing batch-%d / total-%d' % (workdir, int(ceil(float(i+1)/nCurrBatch)), int(ceil(float(len(lTasks))/nCurrBatch)))
			print progress
			emailProgress(progress, lRcvProgress)
			if os.path.exists(fTask):
				os.remove(fTask)
			hTask = open(fTask, 'w')
			for j, line in enumerate(lBatch):
				hTask.write('%s\n' % line)
			hTask.close()
			ret = os.system(cmd)
			progress = '\t[Complete] batch-%d / total-%d' % (int(ceil(float(i+1)/4)), int(ceil(float(len(lTasks))/4)))
			print progress
			emailProgress(progress, lRcvProgress)
			lBatch = []
	if ret == 0:
		progress = '\t[Complete] tracing complete.'
		print progress
		txt = 'workdir = %s\nprogress = %s\n' % (workdir, progress)
		emailProgress(txt, lRcvProgress)


def rawAnalyseSleep(workdir):
	progress =  '[Task] raw sleep analysis of %s' % workdir
	matlab.path(matlab.path(), r'./matlab') # setup matlab env
	print progress
	emailProgress(progress, lRcvProgress)
	while(1):
		# configure light schedule
		isValid = False
		while(1):
			print '\tconfigure light schedule'
			isValid = configTime(workdir)
			if isValid:
				break
		# configure tube order
		isValid = False
		while(1):
			print '\tconfigure tube order'
			isValid = runConfigOrder(workdir)
			if isValid:
				break
		# start raw sleep analysis
		#try:
		matlab.batProcess() # call batchProcess.m
		#except(mlab.matlabcom.MatlabError):
			#print 'Invalid configuration. Please try again.'
			#continue
		break
	progress =  '[Complete] raw sleep analysis of %s' % workdir
	print progress
	emailProgress(progress, lRcvProgress)


def fineAnalyseSleep(workdir):
	progress =  '[Task] fine sleep analysis of %s' % workdir
	matlab.path(matlab.path(), r'./matlab') # setup matlab env
	print progress
	emailProgress(progress, lRcvProgress)
	configDeath('.')
	matlab.fineProcess()
	progress =  '[Complete] fine sleep analysis of %s' % workdir
	print progress
	emailProgress(progress, lRcvProgress)


def summariseSleep(workdir):
	root = tk.Tk()
	root.title(u'sleep summariser')
	rootpath = os.path.join(workdir, workdir.split('\\')[-1])
	app = Application(root, rootpath)
	app.mainloop()
	root.destroy()
	progress =  '[Complete] summarise sleep analysis of %s' % workdir
	print progress
	emailProgress(progress, lRcvProgress)
	


workdir = raw_input('Video directory: ')
#emailProgress('Start new sleep analysis project:\nworkdir= ' + workdir, lRcvProgress)
#renameDav(workdir)
#gatherAll(workdir)
#cvt2Avi(workdir)
lPathGrps = grouping(workdir)
startTracing(workdir)
#rawAnalyseSleep(workdir)
#fineAnalyseSleep(workdir)
#summariseSleep(workdir)
emailProgress('Done. Close project:\nworkdir= ' + workdir, lRcvProgress)