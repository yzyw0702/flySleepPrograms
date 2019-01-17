# coding=utf-8
import numpy as np
import time as tm
import uniout
import cv2
import copy
import scipy.io as sio
from myutils import *


def F_onechannel_SD_R(dirChannel, mTime, mCtTm, minTotalTm, nDaysCT, lenSleep30MinSD, fReport):
	# ���������ļ��嵥
	fOdr = os.path.join(dirChannel, 'txt.order')
	fSpd = os.path.join(dirChannel, 'txt.speed')
	
	# ����.speed��.order����
	mSpd = importMat(fSpd)
	nTmSpd, nFly = np.shape(mSpd) # �����ʱ������λ���룩�͹�Ӭ��ֻ��
	lStkName, lOdr = readOrder(fOdr, fReport)
	nTmCfg = mTime[-1, 1]
	if nTmSpd < nTmCfg: # �ٶ����ݵ���ʱ�� < config_time.txt�е���ʱ��
		msg = '......txt.speed �ļ� %s ��ʱ�� (%d sec) �� config_time.txt �����õ���ʱ�� (%d sec) �̡�\n' % (dirChannel, nTmSpd, nTmCfg)
		printReport(fReport, msg)
		return None
	msg = '......txt.speed ������ɣ�����ߴ� %d x %d\n'  % (nTmSpd, nFly)
	printReport(fReport, msg)
	msg = '......txt.order ������ɣ�'
	printReport(fReport, msg)
	msg = printOdrTable(lStkName, lOdr)
	printReport(fReport, msg)
	
	# ������Ϣ�����ж�ÿһ�����ڹ�Ӭ���˶�������Ϣ
	lenBout = 5 * 60 # ��5������Ϊһ��˯���¼��Ļ�����Ԫ
	kernelTm=cv2.getStructuringElement(cv2.MORPH_RECT,(1, lenBout)) # ��2������Ϊ�ṹԪ�صĳߴ磬1��lenBout�����ǿ�͸ߣ���ÿ5����һ����Ԫ����ƽ������
	mRest = np.zeros(np.shape(mSpd)) # ��Ϣ�����ʼ�����ߴ�Ϊ nTime x nFly��1��������0�����˶�
	mRest[mSpd <= 0] = 1 # �ҵ���Ӭ������ʱ��
	mRest = cv2.morphologyEx(mRest, cv2.MORPH_OPEN, kernelTm)
	
	# �ж�˯��ʱ��֮ǰ�����ж�һ����Ƶĩβ�����������ڣ���Ӭ�Ƿ���˯
	msg = '......��Ϣ '
	printReport(fReport, msg)
	for iFly in range(nFly): # ����ÿһֻ��Ӭ
		if mRest[-1,iFly] == 1: # ֻ���ĩβ����˯�ߵ����
			infoWakeTm = np.where(mRest[:, iFly] == 0) # �ҵ��˶���ʱ��
			lWakeTm = infoWakeTm[0]
			# ���5������ֻҪ�ù�Ӭ���ѹ�һ�Σ�
			if len(lWakeTm) > 0 and len(mRest) - lWakeTm[-1] < lenBout:
				mRest[lWakeTm[-1]:, iFly] = 0 # �ͼ��������¼�
	msg = 'ok, '
	printReport(fReport, msg)
	
	#���ÿ������Ϣʱ��,mRestMinutes, 60��������ݺϲ�;
	msg = '������Ϣ '
	printReport(fReport, msg)
	mRestMinutes=np.zeros((minTotalTm, nFly)) # ÿ������Ϣ���󣬳ߴ�Ϊ nTime/60 x nFly��>0������Ϣʱ������λ���룩
	# sum up data of 60 seconds into that of 1 min
	for iM in range(minTotalTm-1):
		mRestMinutes[iM]=np.sum(mRest[iM*60:(iM+1)*60],axis=0)
	msg = 'ok, '
	printReport(fReport, msg)
	
	#����ÿ30mins��˯��ʱ�����ֱ���CTʱ�仮��30mins(normal sleep ����)�Լ�����¼��ʼÿ30mins����(SD sleep rebount)
	msg = '��Сʱ˯��SD '
	printReport(fReport, msg)
	nFly = len(mRestMinutes[0]) # ��ǰͨ���Ĺ�Ӭ����
	mSleep30MinSD=np.zeros((lenSleep30MinSD, nFly))
	for iHalf in range(lenSleep30MinSD):
		mSleep30MinSD[iHalf]=np.sum(mRestMinutes[iHalf*30:(iHalf+1)*30],axis=0)
	msg = 'ok, '
	printReport(fReport, msg)
	
	#mSleep30MinCT,����CT����ÿ��Сʱ��˯��ˮƽ����һ��ʱ�����<30mins�����Զ�����
	msg = '��Сʱ˯��CT '
	printReport(fReport, msg)
	mSleep30MinCT=np.zeros((nDaysCT * 48, nFly)) - 1 # Ĭ�Ͼ�Ϊ -1
	# i30MinΪ��������ǵڼ���ʱ��㣬ÿ��Сʱһ���㣨��λ����Сʱ��
	i30Min=int(np.ceil(mCtTm[0,1] / 30))
	lSum30MinCT = np.zeros(nFly) # ���ڼ���30����˯���ܳ�
	for iM in range(len(mRestMinutes)):
		lSum30MinCT += mRestMinutes[iM]
		if mCtTm[iM,1] % 30 == 0:
			mSleep30MinCT[i30Min,:] = lSum30MinCT # ��¼��ǰ����
			i30Min += 1 # ׼��������һ����Сʱ
			lSum30MinCT = np.zeros(nFly) # �����ۼ���
	i30Min=int(np.ceil(mCtTm[0,1] / 30))
	# �����һ�׶�ʱ��С��30���ӣ���ȥ��
	if not (mCtTm[0,1]- 1) % 30 == 0:
		mSleep30MinCT[i30Min, :]= -1
	msg = 'ok, '
	printReport(fReport, msg)
	
	# �ٶ����ݽ���
	msg = '������ٶ� '
	printReport(fReport, msg)
	mSpdFine = copy.deepcopy(mSpd) # �������ٶȾ����б��ߴ�Ϊ nTime x nFly
	mSpdFine[0][mSpd[0] == 1] = - 1 # �ѳ�ʼ�ٶȵ���1��ֵ���ı��Ϊ-1
	mSpdFine[mSpdFine >= 10] = - 2 # ���ٶȴ���10�ĵط�����Ϊ-2
	msg = 'ok, '
	printReport(fReport, msg)
	
	#����CT time����30mins speed��ƽ��ֵ
	msg = '30Min�ٶ�CT '
	printReport(fReport,msg)
	mSpdMove = copy.deepcopy(mSpdFine) # ������ÿ���ٶȾ���
	mSpdMove[mSpdFine < 0] = 0 # ���ٶ�С����ĵط����Ϊ 0
	mTimeMove = np.zeros(np.shape(mSpdMove)) # �˶�״̬��ʱ��ֲ�����
	mTimeMove[mSpdFine >= 0] = 1 # �������˶�״̬�ĵط����Ϊ1
	mSpd30MinCT = np.zeros(np.shape(mSleep30MinCT)) - 1 # ��ȱλ�ñ��Ϊ -1
	tSpd = int(np.ceil(mCtTm[0,1] / 30))
	lSumSpdMove = np.zeros((1,nFly))
	lNTmMove = np.zeros((1,nFly))
	for t in range(minTotalTm*60):
		lSumSpdMove += mSpdMove[t,:] # �ۼ��˶�����
		lNTmMove += mTimeMove[t,:] # �ۼ��˶�ʱ��
		if mCtTm[int(np.ceil(t / 60)),1] % 30 == 0 and t%60 == 0: # ÿ30���Ӽ�¼һ������
			for iFly, distance in enumerate(lSumSpdMove[0]):
				if lNTmMove[0,iFly] > 0:
					mSpd30MinCT[tSpd,iFly] = distance / lNTmMove[0,iFly]
				else:
					mSpd30MinCT[tSpd,iFly] = -1
			tSpd += 1
			lSumSpdMove = np.zeros((1,nFly))
			lNTmMove = np.zeros((1,nFly))
	tSpd = int(np.ceil(mCtTm[0,1] / 30))
	if not (mCtTm[0,1] - 1) % 30 == 0: # �����һ��ʱ�䲻��30���ӣ���ȥ��
		mSpd30MinCT[tSpd] = -1
	msg = 'ok, '
	printReport(fReport, msg)
	
	# ����˯�߹�դ�ӱ�
	msg = '˯�߹�դ '
	printReport(fReport, msg)
	nStk = len(lOdr)
	lmRasterPlot_temp=[]
	for iStk, lIdx in enumerate(lOdr):
		lmRasterPlot_temp.append([])
		mRasterPlot = np.zeros((len(mCtTm),len(lIdx) + 1))
		mRasterPlot[:, 0] = mCtTm[:, 0] # ��һ���ǹ�������������=1����ҹ=0��
		lIdx = np.array(lIdx)
		mRasterPlot[:, 1:] = mRestMinutes[:, lIdx - 1]
		lmRasterPlot_temp[-1].append(lStkName[iStk])
		lmRasterPlot_temp[-1].append(mRasterPlot)
	msg = 'ok.\n'
	printReport(fReport, msg)
	
	return mSpd, lStkName, lOdr, mRest, mRestMinutes, mSleep30MinSD, mSleep30MinCT, mSpdFine, mSpd30MinCT, nStk, lmRasterPlot_temp


def F_multichannel_SD_R(dirPath, outputDir):
	# ��������ļ���
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)
	# ���������ļ�
	fReport = os.path.join(outputDir,'report.txt')
	# ��¼ i/o ��Ϣ
	hReport = open(fReport, 'w') # reset report file
	hReport.close()
	msg = '...��ʼ���� '
	printReport(fReport, msg)
	msg = '%s\n' % tm.asctime(tm.localtime(tm.time()))
	printReport(fReport, msg)
	msg = '...�����Ŀ¼Ϊ '
	printReport(fReport, msg)
	msg = '%s\n' % dirPath
	printReport(fReport, msg)
	msg = '...�����Ŀ¼Ϊ '
	printReport(fReport, msg)
	msg = '%s \n' % outputDir
	printReport(fReport, msg)
	# ɨ���������ݼ�
	lFSpd=getAllFiles(dirPath,'txt.speed') # ����ٶ����ݼ��ļ�
	lDirChannel = [f[:-9] for f in lFSpd] # ���ݼ��������ļ����б�
	
	#¼��ʱ����Ϣ,����mTime��¼ʱ��˳��
	fCfgTime=os.path.join(dirPath,'config_time.txt')
	mTime=readTime(fCfgTime,fReport)
	if len(mTime) == 0: # ��� mTime ����ȷ����ֹ����
		msg = '...config_time.txt ���ò���ȷ��\n'
		printReport(fReport, msg)
		return False
	else:
		msg = '...config_time.txt ��������\n'
	printReport(fReport, msg)
	
	# �������ʱ��
	# lTotalTmSpd_tmp��¼�ٶ��ļ���ʱ�� (��λ��min)
	lTotalTmSpd_tmp = [lenSpdFile(fSpd) for fSpd in lFSpd]
	lTotalTmSpd_tmp.append(mTime[-1, 1])
	lTotalTmSpd_tmp = np.array(lTotalTmSpd_tmp)
	minTotalTm = int(np.min(lTotalTmSpd_tmp)) # ����ʱ����Сֵ
	msg = '...\xca\xb1\xbc\xe4\xce\xc4\xbc\xfe\xbc\xec\xb2\xe9\xcd\xea\xb1\xcf,\xbf\xc9\xd3\xc3\xca\xb1\xbc\xe4\xb3\xa4\xb6\xc8\xce\xaa: %d min\n' % minTotalTm
	printReport(fReport, msg)
	
	# ��ʼ�� circadian time table
	mCtTm=np.zeros((minTotalTm,2)) # ����ߴ� nTime x 2
	# ���� ����������
	for t in mTime:
		mCtTm[(t[0]-1):t[1],0]=t[2] # mCtTm ��һ�б�ǰ��죬����
	# ���� ��һ�����ս׶ε�ʱ������
	if mTime[0,2] == 0: # �����ҹ��
		mCtTm[(mTime[0,0]-1):mTime[0,1],1]=np.arange(1440 - (mTime[0,1] - mTime[0,0]+1),1440) # mCtTm �ڶ��б�� CT time /mins
	else: # ����ǰ���
		mCtTm[(mTime[0,0]-1):mTime[0,1],1]=np.arange(720 - (mTime[0,1] - mTime[0,0] + 1),720)
	# ���� ������ս׶ε�ʱ������
	for i,t in enumerate(mTime):
		if i== 0:
			continue
		if t[2] == 0: # ����Ǻ�ҹ
			mCtTm[(t[0]-1):t[1],1]=np.arange(720, 720 + t[1] - t[0] + 1)
		else: # ����ǰ���
			mCtTm[(t[0]-1):t[1],1]=np.arange(0, t[1] - t[0] + 1)
	msg = '...CT\xce\xc4\xbc\xfe\xc9\xfa\xb3\xc9\n'
	printReport(fReport, msg)
	del lTotalTmSpd_tmp
	
	# �����ܹ����ڼ�������
	nDaysCT = 1 
	if mTime[0,2] == 0: # �����һ���׶���ҹ��
		nDaysCT += np.ceil((len(mTime) - 1.0) / 2.0)
	else: # �����һ���׶��ǰ���
		nDaysCT += np.ceil((len(mTime) - 2.0) / 2.0)
	nDaysCT = int(nDaysCT)
	
	# lmSleep30MinSD: �趨SD�汾���ݵ���ʱ��
	lenSleep30MinSD = 48 # SD�����ע���ǵ�1���˯�����ݣ�24Сʱ����48���㣩
	if minTotalTm < 1440: # �����Ƶȫ��С��24Сʱ
		lenSleep30MinSD = np.floor(minTotalTm / 30)
	
	# ����ʱ��͹����������
	fOutTmLight = os.path.join(outputDir, 'main-py_SD_R_raw_time-light.mat')
	if not os.path.exists(fOutTmLight):
		sio.savemat(fOutTmLight, {'mTime':mTime, 'mCtTm':mCtTm, 'nDaysCT':nDaysCT, 'minTotalTm':minTotalTm, 'sourcePath':dirPath })
	else:
		msg = '...ʱ�������ļ��Ѿ����ڡ�'
		printReport(fReport, msg)
	
	# ��¼��ͨ������˯������
	lmRasterPlot = []
	llOdr = []
	llStkName = []
	for iChn, dirChannel in enumerate(lDirChannel):
		sIdxChn = dirChannel.rstrip('\\').split('\\')[-1]
		fOut = os.path.join(outputDir,'main-py_SD_R_ch-%s.mat' % sIdxChn)
		if os.path.exists(fOut):
			msg = '...�����ļ��Ѿ����ڣ��Թ�ͨ�� #'
			printReport(fReport, msg)
			msg = '%s\n' % sIdxChn
			printReport(fReport, msg)
			continue
		msg = '...��ʼ����ͨ�� #'
		printReport(fReport, msg)
		msg = '%s\n' % sIdxChn
		printReport(fReport, msg)
		lTerms = F_onechannel_SD_R(dirChannel, mTime, mCtTm, minTotalTm, nDaysCT, lenSleep30MinSD, fReport)
		if lTerms == None:
			msg = '...��ǰͨ������ʧ�ܣ�������DVR���ݷ�����\n'
			printReport(fReport, msg)
			return False
		mSpd, lStkName, lOdr, mRest, mRestMinutes, mSleep30MinSD, mSleep30MinCT, mSpdFine, mSpd30MinCT, nStk, lmRasterPlot_temp = lTerms
		sio.savemat(fOut, {'nStk':nStk,'mSpd':mSpd,'lStkName':lStkName,'lOdr':lOdr,'mSpdFine':mSpdFine,'mSpd30MinCT':mSpd30MinCT,'mRest':mRest,'mRestMinutes':mRestMinutes,'mSleep30MinSD':mSleep30MinSD,'mSleep30MinCT':mSleep30MinCT})
		lmRasterPlot.extend(lmRasterPlot_temp)
		llOdr.append(lOdr)
		llStkName.append(lStkName)
		del mSpd, lStkName, lOdr, mRest, mRestMinutes, mSleep30MinSD, mSleep30MinCT, mSpdFine, mSpd30MinCT, nStk, lmRasterPlot_temp, lTerms
	
	# ����˯�߹�դͼ
	drawRasterPlot(lmRasterPlot,outputDir)
	msg = '...˯�߹�դͼ�������\n'
	printReport(fReport, msg)
	del lmRasterPlot
	
	# ���ɹ�Ӭ����CT�׶α���ļ� config_flys.txt
	fConfigFly=os.path.join(outputDir,'config_flys.txt')
	if not os.path.exists(fConfigFly):
		hConfigFly=open(fConfigFly,'w')
		hConfigFly.write('line\tindi\tfrag\n')
		for iChn, lOdr in enumerate(llOdr):
			for iStk, lIdx in enumerate(lOdr):
				for iFly in lIdx:
					hConfigFly.write('%d--%s\t' % (iChn, llStkName[iChn][iStk]))
					hConfigFly.write('%d\t' % iStk)
					for iStage in range(len(mTime)):
						hConfigFly.write('%d,' % iStage)
					hConfigFly.write('\n')
		hConfigFly.close()
		msg = '...\xc9\xfa\xb3\xc9jpeg\xcd\xea\xb1\xcf\n'
		printReport(fReport, msg)

	msg = '...\xca\xfd\xbe\xdd\xb1\xa3\xb4\xe6\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	msg='...\xb9\xd8\xb1\xd5\n'
	printReport(fReport, msg)
	return True
	
	
def summarizeData(outputDir):
	fReport = os.path.join(outputDir,'report.txt')
	msg = '...���������ͷ��ౣ������\n'
	printReport(fReport, msg)
	isOk = saveSummaryData(outputDir)
	if not isOk:
		msg = '...�����������ڴ治�㣬��ʹ��matlab�ű���������\n'
		printReport(fReport, msg)
		return
	
	# ����������������
	llOdr = readSummaryData(outputDir, 'llOdr')[0]
	llStkName = readSummaryData(outputDir, 'llStkName')[0]
	fLoadTmLight = os.path.join(outputDir, 'main-py_SD_R_raw_time-light.mat')
	data = sio.loadmat(fLoadTmLight)
	dirPath = data['sourcePath']
	minTotalTm = data['minTotalTm']
	mTime = data['mTime']
	mCtTm = data['mCtTm']
	for k in data.keys():
		del data[k]
	
	# �ܽᲢ�㱨��Ч����
	msg = '...\xca\xfd\xbe\xdd\xb7\xd6\xd7\xe9\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	msg = '...��Ч�����ܽ᣺\n'
	printReport(fReport, msg)
	msg = '......llOdr = \n'
	msg += '.........'
	for iChn, lOdr in enumerate(llOdr):
		for iStk, lIdx in enumerate(lOdr):
			msg += '%s %d->%d; ' % (llStkName[iChn][iStk], lIdx[0], lIdx[-1])
	msg += '\n'
	msg += '......sourcePath = %s\n' % dirPath
	msg += '......minTotalTm = %d (min)\n' % minTotalTm
	msg += '......mTime.shape = %d x %d\n' % np.shape(mTime)
	msg += '......mCtTm.shape = %d x %d\n' % np.shape(mCtTm)
	lmSpd = readSummaryData(outputDir, 'lmSpd')
	msg += summaryOf('lmSpd', lmSpd)
	del lmSpd
	lmSpdFine = readSummaryData(outputDir, 'lmSpdFine')
	msg += summaryOf('lmSpdFine', lmSpdFine)
	del lmSpdFine
	lmSpd30MinCT = readSummaryData(outputDir, 'lmSpd30MinCT')
	msg += summaryOf('lmSpd30MinCT', lmSpd30MinCT)
	del lmSpd30MinCT
	lmRest = readSummaryData(outputDir, 'lmRest')
	msg += summaryOf('lmRest', lmRest)
	del lmRest
	lmRestMinutes = readSummaryData(outputDir, 'lmRestMinutes')
	msg += summaryOf('lmRestMinutes', lmRestMinutes)
	del lmRestMinutes
	lmSleep30MinSD = readSummaryData(outputDir, 'lmSleep30MinSD')
	msg += summaryOf('lmSleep30MinSD', lmSleep30MinSD)
	del lmSleep30MinSD
	lmSleep30MinCT = readSummaryData(outputDir, 'lmSleep30MinCT')
	msg += summaryOf('lmSleep30MinCT', lmSleep30MinCT)
	del lmSleep30MinCT
	printReport(fReport, msg)