# coding=utf-8
import numpy as np
import time as tm
import uniout
import cv2
import copy
import scipy.io as sio
from myutils import *

def F_main_SD_R(dirPath=None,outputDir=None):
	#����ڣ�20140407-09ȫ���ر���
	
	#ʹ�õ���ֵΪ����5mins speed=0��¼Ϊsleep,�м������κ���Ŀ��<=2frames(2secs)������speed��Ϊ0��ȱ��
#���ȱ����������������������ʱ��������>=5mins֮��ſ���ȥ��������
#Ĭ�Ϸ����ӵ�һ���㿪ʼ��������Ŀ,�����Ҫ�޸ģ��봦���ʱ�������ʼ�����ʱ��
	
	#�����Ҫ����ĳһ���ļ��Ľ��������ʱ�����ļ��е�txt.speed����չ���޸�Ϊ��Ķ������������Ը��ļ��Լ�������.location�Լ�.order
	
	#Ϊ����ȷ�ļ������ʳ���λ�ã�¼����Ҫ����һ��������1,ʳ���ڰ��ӵ��м�; 2,���еĹ��Ӷ�Ϊƽ�л��ߴ�ֱ����; 3,ÿһ�����ӵ����Ҷ�����������һ������ʹ�õĹ���
	
	#����ļ���raw plot.jpeg; config_flys.txt����У�������Ĺ�Ӭ, report.txt��¼�������б���,
#'time'_main_SD_R_imported_speed.mat��¼�����.speed���ݺϼ�;
#'time'_main_SD_R_imported_location.mat��¼�����.location���ݺϼ�
#'time'_main_SD_R.mat��¼�����.order����,�Լ��м����ı�������������һ��cell��˵��

	# create output directory
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)
	# set report file
	fReport = os.path.join(outputDir,'report.txt')
	# log i/o info
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
	# set input dataset
	lFSpd=getAllFiles(dirPath,'txt.speed') # speed dataset
	#locationList=[f[:-9] + 'txt.location' for f in lFSpd]
	lFOdr=[f[:-9] + 'txt.order' for f in lFSpd] # order lists
	
	#¼��ʱ����Ϣ,����mTime��¼ʱ��˳��
	fCfgTime=os.path.join(dirPath,'config_time.txt')
	mTime=readTime(fCfgTime,fReport)
	if len(mTime) == 0: # stop program if mTime is invalid
		msg = '...config_time.txt ���ò���ȷ��\n'
	else:
		msg = '...config_time.txt ��������\n'
	printReport(fReport, msg)
	
	#¼�����е�.speed��.order�ļ�
	lmSpd=[]
	llOdr=[]
	llStkName = []
	for i,fSpd in enumerate(lFSpd):
		lmSpd.append(importMat(fSpd))
		nTmSpd, nFlySpd = np.shape(lmSpd[-1]) # get total time of speed data
		lStkName, lOdr = readOrder(lFOdr[i], fReport)
		llStkName.append(lStkName)
		llOdr.append(lOdr)
		nTmCfg = mTime[-1, 1]
		if nTmSpd < nTmCfg: # total time of speed data < time set in config_time.txt
			msg = '......txt.speed �ļ� %s ��ʱ�� (%d sec) �� config_time.txt �����õ���ʱ�� (%d sec) �̡�\n' % (fSpd[:-9], nTmSpd, nTmCfg)
			printReport(fReport, msg)
			return False
		msg = '......' + fSpd
		printReport(fReport, msg)
		msg = ' ������ɡ�����ߴ� %d x %d\n'  % (nTmSpd, nFlySpd)
		printReport(fReport, msg)
		msg = '......txt.order ������ɣ�'
		printReport(fReport, msg)
		msg = printOdrTable(lStkName, lOdr)
		# msg += headOf(lmSpd[-1], 2, 'data-matrix-%d' % i)
		printReport(fReport, msg)
	
	# �������ʱ��
	# lTotalTmSpd_tmp��¼�ٶ��ļ���ʱ�� (��λ��min)
	lTotalTmSpd_tmp = [np.floor(len(mSpd) / 60) for mSpd in lmSpd]
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

	# ������Ϣ�����ж�ÿһ�����ڹ�Ӭ���˶�������Ϣ
	lenBout = 5 * 60 # ��5������Ϊһ��˯���¼��Ļ�����Ԫ
	#��ÿ���ٶȾ�����н���
	lmRest=[] # ��Ϣ�����б��ߴ�Ϊ nChannel x nTime x nFly��1��������0�����˶�
	kernelTm=cv2.getStructuringElement(cv2.MORPH_RECT,(1, lenBout)) # ��2������Ϊ�ṹԪ�صĳߴ磬1��lenBout�����ǿ�͸ߣ���ÿ5����һ����Ԫ����ƽ������
	for i, mSpd in enumerate(lmSpd):
		mSleep_tmp=np.zeros(np.shape(mSpd)) # ��Ϣ�����ʼ��
		mSleep_tmp[mSpd <= 0]=1 # �ҵ���Ӭ������ʱ��
		mSleep_tmp = cv2.morphologyEx(mSleep_tmp, cv2.MORPH_OPEN, kernelTm)
		lmRest.append(mSleep_tmp)
	#�����ж�˯��ʱ��֮ǰ�����ж�һ����Ƶĩβ�����������ڣ���Ӭ�Ƿ���˯
	for iChn, mRest in enumerate(lmRest): # ����ÿһ��¼��ͨ��
		nFly = len(mRest[0]) # ��ǰͨ���Ĺ�Ӭ����
		for iFly in range(nFly): # ����ÿһֻ��Ӭ
			if mRest[-1,iFly] == 1: # ֻ���ĩβ����˯�ߵ����
				infoWakeTm = np.where(mRest[:, iFly] == 0) # �ҵ��˶���ʱ��
				lWakeTm = infoWakeTm[0]
				# ���5������ֻҪ�ù�Ӭ���ѹ�һ�Σ�
				if len(lWakeTm) > 0 and len(mRest) - lWakeTm[-1] < lenBout:
					lmRest[iChn][lWakeTm[-1]:, iFly] = 0 # �ͼ��������¼�
	msg = '...��Ӭ��Ϣ���ݼ������\n'
	printReport(fReport, msg)
	
	#���ÿ������Ϣʱ��,lmRestMinutes, 60��������ݺϲ�;
	lmRestMinutes=[] # ÿ������Ϣ�����б��ߴ�Ϊ nChannel x nTime/60 x nFly��>0������Ϣʱ������λ���룩
	for iChn, mRest in enumerate(lmRest):
		nFly = len(mRest[0]) # ��ǰͨ���Ĺ�Ӭ����
		mRestMinutes=np.zeros((minTotalTm, nFly))
		# sum up data of 60 seconds into that of 1 min
		for iM in range(minTotalTm-1):
			mRestMinutes[iM]=np.sum(mRest[iM*60:(iM+1)*60],axis=0)
		lmRestMinutes.append(mRestMinutes)
	msg = '...��Ӭÿ������Ϣ���ݼ������\n'
	printReport(fReport, msg)

	#����ÿ30mins��˯��ʱ�����ֱ���CTʱ�仮��30mins(normal sleep ����)�Լ�����¼��ʼÿ30mins����(SD sleep rebount)
	#lmSleep30MinSD: max calculated length 24hours
	lmSleep30MinSD=[] # ÿ��Сʱ��˯�߾����б��ߴ�Ϊ nChannel x nTime/1800 x nFly��>0����˯��ʱ������λ���룩
	lenSleep30MinSD = 48 # SD�����ע���ǵ�1���˯�����ݣ�24Сʱ����48���㣩
	if minTotalTm < 1440: # �����Ƶȫ��С��24Сʱ
		lenSleep30MinSD = np.floor(minTotalTm / 30)
	for iChn, mRestMinutes in enumerate(lmRestMinutes):
		nFly = len(mRestMinutes[0]) # ��ǰͨ���Ĺ�Ӭ����
		mSleep30MinSD=np.zeros((lenSleep30MinSD, nFly))
		for iHalf in range(lenSleep30MinSD):
			mSleep30MinSD[iHalf]=np.sum(mRestMinutes[iHalf*30:(iHalf+1)*30],axis=0)
		lmSleep30MinSD.append(mSleep30MinSD)
	msg = '...��Ӭÿ��Сʱ˯�����ݣ�SD�汾���������\n'
	printReport(fReport, msg)
	
	# �����ܹ����ڼ�������
	nDaysCT = 1 
	if mTime[0,2] == 0: # �����һ���׶���ҹ��
		nDaysCT += np.ceil((len(mTime) - 1.0) / 2.0)
	else: # �����һ���׶��ǰ���
		nDaysCT += np.ceil((len(mTime) - 2.0) / 2.0)
	nDaysCT = int(nDaysCT)
	#lmSleep30MinCT,����CT����ÿ��Сʱ��˯��ˮƽ����һ��ʱ�����<30mins�����Զ�����
	lmSleep30MinCT=[]
	for iChn, mRestMinutes in enumerate(lmRestMinutes):
		nFly = len(mRestMinutes[0]) # ��ǰͨ���Ĺ�Ӭ����
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
		lmSleep30MinCT.append(mSleep30MinCT)
	msg = '...��Ӭÿ��Сʱ˯�����ݣ�CT�汾���������\n'
	printReport(fReport, msg)
	
	#���õ������� lmRest(�ж�ÿһ���Ƿ���˯��); lmRestMinutesΪÿһ����˯�����ݣ�����������jpeg raw sleepͼ
#lmSleep30MinSD ����¼��ʼÿ30mins����(SD sleep rebount),  lmSleep30MinCT ����CTʱ�仮��30mins(normal sleep ����)
## ����.speed ���ݣ������˶��ٶ�,����ÿ���Ӻϲ����Լ�ÿ30mins�ϲ�
# ��speed ���ݾ������룬��Ϊtrace������ʱ������������һ���������ֵ��������ʱ��������speed>=10 �� point��
	lmSpdFine=[] # �������ٶȾ����б��ߴ�Ϊ nChannel x nTime x nFly
	for iChn, mSpd in enumerate(lmSpd):
		mSpdFine=mSpd
		mSpdFine[0][mSpd[0] == 1] = - 1 # �ѳ�ʼ�ٶȵ���1��ֵ���ı��Ϊ-1
		mSpdFine[mSpdFine >= 10] = - 2 # ���ٶȴ���10�ĵط�����Ϊ-2
		lmSpdFine.append(mSpdFine)
	msg = '...�����Ĺ�Ӭ�ٶ����ݼ������\n'
	printReport(fReport, msg)
	#����CT time����30mins֮��speed��ƽ��ֵ
	lmSpd30MinCT=[] # 30�����ٶȾ����б�CT�汾�����ߴ�Ϊ nChannel x nTime x nFly
	for iChn, mSpdFine in enumerate(lmSpdFine):
		nFly = len(mSpdFine[0])
		mSpdMove = copy.deepcopy(mSpdFine) # ������ÿ���ٶȾ���
		mSpdMove[mSpdFine < 0] = 0 # ���ٶ�С����ĵط����Ϊ 0
		mTimeMove = np.zeros(np.shape(mSpdMove)) # �˶�״̬��ʱ��ֲ�����
		mTimeMove[mSpdFine >= 0] = 1 # �������˶�״̬�ĵط����Ϊ1
		mSpd30MinCT = np.zeros(np.shape(lmSleep30MinCT[iChn])) - 1 # ��ȱλ�ñ��Ϊ -1
		tSpd = int(np.ceil(mCtTm[0,1] / 30))
		lSumSpdMove = np.zeros((1,nFly))
		lNTmMove = np.zeros((1,nFly))
		for t in range(minTotalTm*60):
			lSumSpdMove += mSpdMove[t,:] # �ۼ��˶�����
			lNTmMove += mTimeMove[t,:] # �ۼ��˶�ʱ��
			if mCtTm[int(np.ceil(t / 60)),1] % 30 == 0 and t%60 == 0: # ÿ30���Ӽ�¼һ������
				for iFly, distance in enumerate(lSumSpdMove[0]):
					if lNTmMove[0,iFly] > 0:
						mSpd30MinCT[tSpd,iFly]=lSumSpdMove[0,iFly] / lNTmMove[0,iFly]
					else:
						mSpd30MinCT[tSpd,iFly] = -1
				tSpd += 1
				lSumSpdMove = np.zeros((1,nFly))
				lNTmMove = np.zeros((1,nFly))
		tSpd = int(np.ceil(mCtTm[0,1] / 30))
		if not (mCtTm[0,1] - 1) % 30 == 0: # �����һ��ʱ�䲻��30���ӣ���ȥ��
			mSpd30MinCT[tSpd] = -1
		lmSpd30MinCT.append(mSpd30MinCT)
		msg = '......�� %d ���ļ���30Min�˶��ٶ����ݣ�CT�汾��������ϡ�\n' % (iChn+1)
		printReport(fReport,msg)
	# ���浼����ٶ�����
	fOutSpd = os.path.join(outputDir,'main-py_SD_R_imported_speed.mat')
	sio.savemat(fOutSpd, {'lmSpd': lmSpd})
	# return True

	# ����˯�߹�դͼ
	nStk=0 # ����Ʒϵ��Ŀ,nStk
	lmRasterPlot = []
	for iChn in range(len(lFSpd)):
		nStk += len(llOdr[iChn])
		lmRasterPlot_temp=[]
		for iStk, lIdx in enumerate(llOdr[iChn]):
			lmRasterPlot_temp.append([])
			mRasterPlot = np.zeros((len(mCtTm),len(lIdx) + 1))
			mRasterPlot[:, 0] = mCtTm[:, 0] # ��һ���ǹ�������������=1����ҹ=0��
			lIdx = np.array(lIdx)
			mRasterPlot[:, 1:] = lmRestMinutes[iChn][:, lIdx - 1]
			lmRasterPlot_temp[-1].append(llStkName[iChn][iStk])
			lmRasterPlot_temp[-1].append(mRasterPlot)
		lmRasterPlot.extend(lmRasterPlot_temp)
	drawRasterPlot(lmRasterPlot,outputDir)
	msg = '...˯�߹�դͼ�������\n'
	printReport(fReport, msg)
	
	# ���ɹ�Ӭ����CT�׶α���ļ� config_flys.txt
	fConfigFly=os.path.join(outputDir,'config_flys.txt')
	hConfigFly=open(fConfigFly,'w')
	hConfigFly.write('line\tindi\tfrag\n')
	for iChn, lOdr in enumerate(llOdr):
		for iStk, lIdx in enumerate(lOdr):
			for iFly in lIdx:
				hConfigFly.write('%d--%s\t' % (iChn, lmRasterPlot[iChn][0]))
				hConfigFly.write('%d\t' % iStk)
				for iStage in range(len(mTime)):
					hConfigFly.write('%d,' % iStage)
				hConfigFly.write('\n')
	hConfigFly.close()
	msg = '...\xc9\xfa\xb3\xc9jpeg\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)

	# �ܽᲢ�㱨��Ч����
	msg = '...\xca\xfd\xbe\xdd\xb7\xd6\xd7\xe9\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	msg = '...��Ч�����ܽ᣺\n'
	printReport(fReport, msg)
	msg = '......llOdr = \n'
	for iChn, lOdr in enumerate(llOdr):
		for iStk, lIdx in enumerate(lOdr):
			msg += '.........%s\t%d->%d\n' % (llStkName[iChn][iStk], lIdx[0], lIdx[-1])
	msg += '......sourcePath = %s\n' % dirPath
	msg += '......minTotalTm = %d (min)\n' % minTotalTm
	msg += '......mTime.shape = %d x %d\n' % np.shape(mTime)
	msg += '......mCtTm.shape = %d x %d\n' % np.shape(mCtTm)
	msg += summaryOf('lmSpdFine', lmSpdFine)
	msg += summaryOf('lmSpd30MinCT', lmSpd30MinCT)
	msg += summaryOf('lmRest', lmRest)
	msg += summaryOf('lmRestMinutes', lmRestMinutes)
	msg += summaryOf('lmSleep30MinSD', lmSleep30MinSD)
	msg += summaryOf('lmSleep30MinCT', lmSleep30MinCT)
	printReport(fReport, msg)

	# ������Ч����
	fOutAll = os.path.join(outputDir,'main-py_SD_R.mat')
	sio.savemat(fOutAll, {'sourcePath':dirPath, 'mTime':mTime, 'mCtTm':mCtTm, 'minTotalTm':minTotalTm, 'llStkName':llStkName,'llOdr':llOdr,'lmSpdFine':lmSpdFine,'lmSpd30MinCT':lmSpd30MinCT,'lmRest':lmRest,'lmRestMinutes':lmRestMinutes,'lmSleep30MinSD':lmSleep30MinSD,'lmSleep30MinCT':lmSleep30MinCT})
	msg = '...\xca\xfd\xbe\xdd\xb1\xa3\xb4\xe6\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	
	msg='...\xb9\xd8\xb1\xd5\n'
	printReport(fReport, msg)
	return True

	


def F_onechannel_SD_R(dirChannel, iChn, mTime, mCtTm, minTotalTm, nDaysCT, lenSleep30MinSD, fReport):
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
	msg = '......' + fSpd
	printReport(fReport, msg)
	msg = ' ������ɡ�����ߴ� %d x %d\n'  % (nTmSpd, nFly)
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
	for iFly in range(nFly): # ����ÿһֻ��Ӭ
		if mRest[-1,iFly] == 1: # ֻ���ĩβ����˯�ߵ����
			infoWakeTm = np.where(mRest[:, iFly] == 0) # �ҵ��˶���ʱ��
			lWakeTm = infoWakeTm[0]
			# ���5������ֻҪ�ù�Ӭ���ѹ�һ�Σ�
			if len(lWakeTm) > 0 and len(mRest) - lWakeTm[-1] < lenBout:
				mRest[lWakeTm[-1]:, iFly] = 0 # �ͼ��������¼�
	msg = '......��Ӭ��Ϣ���ݼ������\n'
	printReport(fReport, msg)
	
	#���ÿ������Ϣʱ��,mRestMinutes, 60��������ݺϲ�;
	mRestMinutes=np.zeros((minTotalTm, nFly)) # ÿ������Ϣ���󣬳ߴ�Ϊ nTime/60 x nFly��>0������Ϣʱ������λ���룩
	# sum up data of 60 seconds into that of 1 min
	for iM in range(minTotalTm-1):
		mRestMinutes[iM]=np.sum(mRest[iM*60:(iM+1)*60],axis=0)
	msg = '......��Ӭÿ������Ϣ���ݼ������\n'
	printReport(fReport, msg)
	
	#����ÿ30mins��˯��ʱ�����ֱ���CTʱ�仮��30mins(normal sleep ����)�Լ�����¼��ʼÿ30mins����(SD sleep rebount)
	nFly = len(mRestMinutes[0]) # ��ǰͨ���Ĺ�Ӭ����
	mSleep30MinSD=np.zeros((lenSleep30MinSD, nFly))
	for iHalf in range(lenSleep30MinSD):
		mSleep30MinSD[iHalf]=np.sum(mRestMinutes[iHalf*30:(iHalf+1)*30],axis=0)
	msg = '......��Ӭÿ��Сʱ˯�����ݣ�SD�汾���������\n'
	printReport(fReport, msg)
	
	#mSleep30MinCT,����CT����ÿ��Сʱ��˯��ˮƽ����һ��ʱ�����<30mins�����Զ�����
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
	msg = '......��Ӭÿ��Сʱ˯�����ݣ�CT�汾���������\n'
	printReport(fReport, msg)
	
	# �ٶ����ݽ���
	mSpdFine = copy.deepcopy(mSpd) # �������ٶȾ����б��ߴ�Ϊ nTime x nFly
	mSpdFine[0][mSpd[0] == 1] = - 1 # �ѳ�ʼ�ٶȵ���1��ֵ���ı��Ϊ-1
	mSpdFine[mSpdFine >= 10] = - 2 # ���ٶȴ���10�ĵط�����Ϊ-2
	msg = '......�����Ĺ�Ӭ�ٶ����ݼ������\n'
	printReport(fReport, msg)
	
	#����CT time����30mins speed��ƽ��ֵ
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
	msg = '......30Min�˶��ٶ����ݣ�CT�汾��������ϡ�\n'
	printReport(fReport,msg)
	
	# ����˯�߹�դͼ�ӱ�
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
	msg = '......˯�߹�դͼ�ӱ��������\n'
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
	
	#lmSleep30MinSD: �趨SD�汾���ݵ���ʱ��
	lenSleep30MinSD = 48 # SD�����ע���ǵ�1���˯�����ݣ�24Сʱ����48���㣩
	if minTotalTm < 1440: # �����Ƶȫ��С��24Сʱ
		lenSleep30MinSD = np.floor(minTotalTm / 30)
	
	# ��¼��ͨ������˯������
	nTotalStk = 0
	lmSpd = []
	llStkName = []
	llOdr = []
	lmRest = []
	lmRestMinutes = []
	lmSleep30MinSD = []
	lmSleep30MinCT = []
	lmSpdFine = []
	lmSpd30MinCT = []
	lmRasterPlot = []
	for iChn, dirChannel in enumerate(lDirChannel):
		mSpd, lStkName, lOdr, mRest, mRestMinutes, mSleep30MinSD, mSleep30MinCT, mSpdFine, mSpd30MinCT, nStk, lmRasterPlot_temp = F_onechannel_SD_R(dirChannel, iChn, mTime, mCtTm, minTotalTm, nDaysCT, lenSleep30MinSD, fReport)
		lmSpd.append(mSpd)
		llStkName.append(lStkName)
		llOdr.append(lOdr)
		lmRest.append(mRest)
		lmRestMinutes.append(mRestMinutes)
		lmSleep30MinSD.append(mSleep30MinSD)
		lmSleep30MinCT.append(mSleep30MinCT)
		lmSpdFine.append(mSpdFine)
		lmSpd30MinCT.append(mSpd30MinCT)
		nTotalStk += nStk
		lmRasterPlot.extend(lmRasterPlot_temp)
	
	# ���浼����ٶ�����
	fOutSpd = os.path.join(outputDir,'main-py_SD_R_imported_speed.mat')
	sio.savemat(fOutSpd, {'lmSpd': lmSpd})
	
	# ����˯�߹�դͼ
	drawRasterPlot(lmRasterPlot,outputDir)
	msg = '...˯�߹�դͼ�������\n'
	printReport(fReport, msg)
	
	# ���ɹ�Ӭ����CT�׶α���ļ� config_flys.txt
	fConfigFly=os.path.join(outputDir,'config_flys.txt')
	hConfigFly=open(fConfigFly,'w')
	hConfigFly.write('line\tindi\tfrag\n')
	for iChn, lOdr in enumerate(llOdr):
		for iStk, lIdx in enumerate(lOdr):
			for iFly in lIdx:
				hConfigFly.write('%d--%s\t' % (iChn, lmRasterPlot[iChn][0]))
				hConfigFly.write('%d\t' % iStk)
				for iStage in range(len(mTime)):
					hConfigFly.write('%d,' % iStage)
				hConfigFly.write('\n')
	hConfigFly.close()
	msg = '...\xc9\xfa\xb3\xc9jpeg\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	
	# �ܽᲢ�㱨��Ч����
	msg = '...\xca\xfd\xbe\xdd\xb7\xd6\xd7\xe9\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	msg = '...��Ч�����ܽ᣺\n'
	printReport(fReport, msg)
	msg = '......llOdr = \n'
	for iChn, lOdr in enumerate(llOdr):
		for iStk, lIdx in enumerate(lOdr):
			msg += '.........%s\t%d->%d\n' % (llStkName[iChn][iStk], lIdx[0], lIdx[-1])
	msg += '......sourcePath = %s\n' % dirPath
	msg += '......minTotalTm = %d (min)\n' % minTotalTm
	msg += '......mTime.shape = %d x %d\n' % np.shape(mTime)
	msg += '......mCtTm.shape = %d x %d\n' % np.shape(mCtTm)
	msg += summaryOf('lmSpdFine', lmSpdFine)
	msg += summaryOf('lmSpd30MinCT', lmSpd30MinCT)
	msg += summaryOf('lmRest', lmRest)
	msg += summaryOf('lmRestMinutes', lmRestMinutes)
	msg += summaryOf('lmSleep30MinSD', lmSleep30MinSD)
	msg += summaryOf('lmSleep30MinCT', lmSleep30MinCT)
	printReport(fReport, msg)

	# ������Ч����
	fOutAll = os.path.join(outputDir,'main-py_SD_R.mat')
	sio.savemat(fOutAll, {'sourcePath':dirPath, 'mTime':mTime, 'mCtTm':mCtTm, 'minTotalTm':minTotalTm, 'llStkName':llStkName,'llOdr':llOdr,'lmSpdFine':lmSpdFine,'lmSpd30MinCT':lmSpd30MinCT,'lmRest':lmRest,'lmRestMinutes':lmRestMinutes,'lmSleep30MinSD':lmSleep30MinSD,'lmSleep30MinCT':lmSleep30MinCT})
	msg = '...\xca\xfd\xbe\xdd\xb1\xa3\xb4\xe6\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	
	msg='...\xb9\xd8\xb1\xd5\n'
	printReport(fReport, msg)
	return True
	
	