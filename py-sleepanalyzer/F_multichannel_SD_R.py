# coding=utf-8
import numpy as np
import time as tm
import uniout
import cv2
import copy
import scipy.io as sio
from myutils import *


def F_onechannel_SD_R(dirChannel, mTime, mCtTm, minTotalTm, nDaysCT, lenSleep30MinSD, fReport):
	# 整理输入文件清单
	fOdr = os.path.join(dirChannel, 'txt.order')
	fSpd = os.path.join(dirChannel, 'txt.speed')
	
	# 导入.speed和.order数据
	mSpd = importMat(fSpd)
	nTmSpd, nFly = np.shape(mSpd) # 获得总时长（单位：秒）和果蝇总只数
	lStkName, lOdr = readOrder(fOdr, fReport)
	nTmCfg = mTime[-1, 1]
	if nTmSpd < nTmCfg: # 速度数据的总时长 < config_time.txt中的总时长
		msg = '......txt.speed 文件 %s 总时长 (%d sec) 比 config_time.txt 中设置的总时间 (%d sec) 短。\n' % (dirChannel, nTmSpd, nTmCfg)
		printReport(fReport, msg)
		return None
	msg = '......txt.speed 导入完成，矩阵尺寸 %d x %d\n'  % (nTmSpd, nFly)
	printReport(fReport, msg)
	msg = '......txt.order 导入完成：'
	printReport(fReport, msg)
	msg = printOdrTable(lStkName, lOdr)
	printReport(fReport, msg)
	
	# 计算休息矩阵：判断每一秒钟内果蝇是运动还是休息
	lenBout = 5 * 60 # 以5分钟作为一个睡眠事件的基本单元
	kernelTm=cv2.getStructuringElement(cv2.MORPH_RECT,(1, lenBout)) # 第2个参数为结构元素的尺寸，1和lenBout依次是宽和高，即每5分钟一个单元进行平滑处理
	mRest = np.zeros(np.shape(mSpd)) # 休息矩阵初始化，尺寸为 nTime x nFly；1代表不动，0代表运动
	mRest[mSpd <= 0] = 1 # 找到果蝇不动的时刻
	mRest = cv2.morphologyEx(mRest, cv2.MORPH_OPEN, kernelTm)
	
	# 判定睡眠时间之前，先判断一下视频末尾的最后五分钟内，果蝇是否在睡
	msg = '......休息 '
	printReport(fReport, msg)
	for iFly in range(nFly): # 对于每一只果蝇
		if mRest[-1,iFly] == 1: # 只针对末尾处于睡眠的情况
			infoWakeTm = np.where(mRest[:, iFly] == 0) # 找到运动的时刻
			lWakeTm = infoWakeTm[0]
			# 最后5分钟内只要该果蝇清醒过一次，
			if len(lWakeTm) > 0 and len(mRest) - lWakeTm[-1] < lenBout:
				mRest[lWakeTm[-1]:, iFly] = 0 # 就记作清醒事件
	msg = 'ok, '
	printReport(fReport, msg)
	
	#获得每分钟休息时长,mRestMinutes, 60个点的数据合并;
	msg = '分钟休息 '
	printReport(fReport, msg)
	mRestMinutes=np.zeros((minTotalTm, nFly)) # 每分钟休息矩阵，尺寸为 nTime/60 x nFly；>0代表休息时长（单位：秒）
	# sum up data of 60 seconds into that of 1 min
	for iM in range(minTotalTm-1):
		mRestMinutes[iM]=np.sum(mRest[iM*60:(iM+1)*60],axis=0)
	msg = 'ok, '
	printReport(fReport, msg)
	
	#计算每30mins的睡眠时长，分别按照CT时间划分30mins(normal sleep 分析)以及按照录像开始每30mins划分(SD sleep rebount)
	msg = '半小时睡眠SD '
	printReport(fReport, msg)
	nFly = len(mRestMinutes[0]) # 当前通道的果蝇个数
	mSleep30MinSD=np.zeros((lenSleep30MinSD, nFly))
	for iHalf in range(lenSleep30MinSD):
		mSleep30MinSD[iHalf]=np.sum(mRestMinutes[iHalf*30:(iHalf+1)*30],axis=0)
	msg = 'ok, '
	printReport(fReport, msg)
	
	#mSleep30MinCT,按照CT计算每半小时的睡眠水平，第一段时间如果<30mins，将自动忽略
	msg = '半小时睡眠CT '
	printReport(fReport, msg)
	mSleep30MinCT=np.zeros((nDaysCT * 48, nFly)) - 1 # 默认均为 -1
	# i30Min为待处理的是第几个时间点，每半小时一个点（单位：半小时）
	i30Min=int(np.ceil(mCtTm[0,1] / 30))
	lSum30MinCT = np.zeros(nFly) # 用于计算30分钟睡眠总长
	for iM in range(len(mRestMinutes)):
		lSum30MinCT += mRestMinutes[iM]
		if mCtTm[iM,1] % 30 == 0:
			mSleep30MinCT[i30Min,:] = lSum30MinCT # 记录当前数据
			i30Min += 1 # 准备计算下一个半小时
			lSum30MinCT = np.zeros(nFly) # 重置累加器
	i30Min=int(np.ceil(mCtTm[0,1] / 30))
	# 如果第一阶段时间小于30分钟，则去除
	if not (mCtTm[0,1]- 1) % 30 == 0:
		mSleep30MinCT[i30Min, :]= -1
	msg = 'ok, '
	printReport(fReport, msg)
	
	# 速度数据降噪
	msg = '降噪后速度 '
	printReport(fReport, msg)
	mSpdFine = copy.deepcopy(mSpd) # 降噪后的速度矩阵列表，尺寸为 nTime x nFly
	mSpdFine[0][mSpd[0] == 1] = - 1 # 把初始速度等于1的值都改标记为-1
	mSpdFine[mSpdFine >= 10] = - 2 # 把速度大于10的地方都标为-2
	msg = 'ok, '
	printReport(fReport, msg)
	
	#依据CT time计算30mins speed的平均值
	msg = '30Min速度CT '
	printReport(fReport,msg)
	mSpdMove = copy.deepcopy(mSpdFine) # 降噪后的每秒速度矩阵
	mSpdMove[mSpdFine < 0] = 0 # 将速度小于零的地方标记为 0
	mTimeMove = np.zeros(np.shape(mSpdMove)) # 运动状态的时间分布矩阵
	mTimeMove[mSpdFine >= 0] = 1 # 将处于运动状态的地方标记为1
	mSpd30MinCT = np.zeros(np.shape(mSleep30MinCT)) - 1 # 空缺位置标记为 -1
	tSpd = int(np.ceil(mCtTm[0,1] / 30))
	lSumSpdMove = np.zeros((1,nFly))
	lNTmMove = np.zeros((1,nFly))
	for t in range(minTotalTm*60):
		lSumSpdMove += mSpdMove[t,:] # 累加运动距离
		lNTmMove += mTimeMove[t,:] # 累加运动时长
		if mCtTm[int(np.ceil(t / 60)),1] % 30 == 0 and t%60 == 0: # 每30分钟记录一次数据
			for iFly, distance in enumerate(lSumSpdMove[0]):
				if lNTmMove[0,iFly] > 0:
					mSpd30MinCT[tSpd,iFly] = distance / lNTmMove[0,iFly]
				else:
					mSpd30MinCT[tSpd,iFly] = -1
			tSpd += 1
			lSumSpdMove = np.zeros((1,nFly))
			lNTmMove = np.zeros((1,nFly))
	tSpd = int(np.ceil(mCtTm[0,1] / 30))
	if not (mCtTm[0,1] - 1) % 30 == 0: # 如果第一段时间不足30分钟，则去除
		mSpd30MinCT[tSpd] = -1
	msg = 'ok, '
	printReport(fReport, msg)
	
	# 生成睡眠光栅子表
	msg = '睡眠光栅 '
	printReport(fReport, msg)
	nStk = len(lOdr)
	lmRasterPlot_temp=[]
	for iStk, lIdx in enumerate(lOdr):
		lmRasterPlot_temp.append([])
		mRasterPlot = np.zeros((len(mCtTm),len(lIdx) + 1))
		mRasterPlot[:, 0] = mCtTm[:, 0] # 第一列是光照条件（白天=1，黑夜=0）
		lIdx = np.array(lIdx)
		mRasterPlot[:, 1:] = mRestMinutes[:, lIdx - 1]
		lmRasterPlot_temp[-1].append(lStkName[iStk])
		lmRasterPlot_temp[-1].append(mRasterPlot)
	msg = 'ok.\n'
	printReport(fReport, msg)
	
	return mSpd, lStkName, lOdr, mRest, mRestMinutes, mSleep30MinSD, mSleep30MinCT, mSpdFine, mSpd30MinCT, nStk, lmRasterPlot_temp


def F_multichannel_SD_R(dirPath, outputDir):
	# 创建输出文件夹
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)
	# 创建报告文件
	fReport = os.path.join(outputDir,'report.txt')
	# 记录 i/o 信息
	hReport = open(fReport, 'w') # reset report file
	hReport.close()
	msg = '...开始分析 '
	printReport(fReport, msg)
	msg = '%s\n' % tm.asctime(tm.localtime(tm.time()))
	printReport(fReport, msg)
	msg = '...输入根目录为 '
	printReport(fReport, msg)
	msg = '%s\n' % dirPath
	printReport(fReport, msg)
	msg = '...输出根目录为 '
	printReport(fReport, msg)
	msg = '%s \n' % outputDir
	printReport(fReport, msg)
	# 扫描输入数据集
	lFSpd=getAllFiles(dirPath,'txt.speed') # 获得速度数据集文件
	lDirChannel = [f[:-9] for f in lFSpd] # 数据集所在子文件夹列表
	
	#录入时间信息,生成mTime记录时间顺序
	fCfgTime=os.path.join(dirPath,'config_time.txt')
	mTime=readTime(fCfgTime,fReport)
	if len(mTime) == 0: # 如果 mTime 不正确，中止程序
		msg = '...config_time.txt 设置不正确。\n'
		printReport(fReport, msg)
		return False
	else:
		msg = '...config_time.txt 正常加载\n'
	printReport(fReport, msg)
	
	# 计算最短时长
	# lTotalTmSpd_tmp记录速度文件总时长 (单位：min)
	lTotalTmSpd_tmp = [lenSpdFile(fSpd) for fSpd in lFSpd]
	lTotalTmSpd_tmp.append(mTime[-1, 1])
	lTotalTmSpd_tmp = np.array(lTotalTmSpd_tmp)
	minTotalTm = int(np.min(lTotalTmSpd_tmp)) # 求总时长最小值
	msg = '...\xca\xb1\xbc\xe4\xce\xc4\xbc\xfe\xbc\xec\xb2\xe9\xcd\xea\xb1\xcf,\xbf\xc9\xd3\xc3\xca\xb1\xbc\xe4\xb3\xa4\xb6\xc8\xce\xaa: %d min\n' % minTotalTm
	printReport(fReport, msg)
	
	# 初始化 circadian time table
	mCtTm=np.zeros((minTotalTm,2)) # 矩阵尺寸 nTime x 2
	# 生成 光照条件列
	for t in mTime:
		mCtTm[(t[0]-1):t[1],0]=t[2] # mCtTm 第一列标记白天，晚上
	# 生成 第一个光照阶段的时间序列
	if mTime[0,2] == 0: # 如果是夜晚
		mCtTm[(mTime[0,0]-1):mTime[0,1],1]=np.arange(1440 - (mTime[0,1] - mTime[0,0]+1),1440) # mCtTm 第二列标记 CT time /mins
	else: # 如果是白天
		mCtTm[(mTime[0,0]-1):mTime[0,1],1]=np.arange(720 - (mTime[0,1] - mTime[0,0] + 1),720)
	# 生成 其余光照阶段的时间序列
	for i,t in enumerate(mTime):
		if i== 0:
			continue
		if t[2] == 0: # 如果是黑夜
			mCtTm[(t[0]-1):t[1],1]=np.arange(720, 720 + t[1] - t[0] + 1)
		else: # 如果是白天
			mCtTm[(t[0]-1):t[1],1]=np.arange(0, t[1] - t[0] + 1)
	msg = '...CT\xce\xc4\xbc\xfe\xc9\xfa\xb3\xc9\n'
	printReport(fReport, msg)
	del lTotalTmSpd_tmp
	
	# 计算总共存在几个白天
	nDaysCT = 1 
	if mTime[0,2] == 0: # 如果第一个阶段是夜晚
		nDaysCT += np.ceil((len(mTime) - 1.0) / 2.0)
	else: # 如果第一个阶段是白天
		nDaysCT += np.ceil((len(mTime) - 2.0) / 2.0)
	nDaysCT = int(nDaysCT)
	
	# lmSleep30MinSD: 设定SD版本数据的总时长
	lenSleep30MinSD = 48 # SD后最关注的是第1天的睡眠数据（24小时，共48个点）
	if minTotalTm < 1440: # 如果视频全长小于24小时
		lenSleep30MinSD = np.floor(minTotalTm / 30)
	
	# 保存时间和光照相关数据
	fOutTmLight = os.path.join(outputDir, 'main-py_SD_R_raw_time-light.mat')
	if not os.path.exists(fOutTmLight):
		sio.savemat(fOutTmLight, {'mTime':mTime, 'mCtTm':mCtTm, 'nDaysCT':nDaysCT, 'minTotalTm':minTotalTm, 'sourcePath':dirPath })
	else:
		msg = '...时间数据文件已经存在。'
		printReport(fReport, msg)
	
	# 分录像通道分析睡眠数据
	lmRasterPlot = []
	llOdr = []
	llStkName = []
	for iChn, dirChannel in enumerate(lDirChannel):
		sIdxChn = dirChannel.rstrip('\\').split('\\')[-1]
		fOut = os.path.join(outputDir,'main-py_SD_R_ch-%s.mat' % sIdxChn)
		if os.path.exists(fOut):
			msg = '...数据文件已经存在，略过通道 #'
			printReport(fReport, msg)
			msg = '%s\n' % sIdxChn
			printReport(fReport, msg)
			continue
		msg = '...开始分析通道 #'
		printReport(fReport, msg)
		msg = '%s\n' % sIdxChn
		printReport(fReport, msg)
		lTerms = F_onechannel_SD_R(dirChannel, mTime, mCtTm, minTotalTm, nDaysCT, lenSleep30MinSD, fReport)
		if lTerms == None:
			msg = '...当前通道处理失败，结束该DVR数据分析。\n'
			printReport(fReport, msg)
			return False
		mSpd, lStkName, lOdr, mRest, mRestMinutes, mSleep30MinSD, mSleep30MinCT, mSpdFine, mSpd30MinCT, nStk, lmRasterPlot_temp = lTerms
		sio.savemat(fOut, {'nStk':nStk,'mSpd':mSpd,'lStkName':lStkName,'lOdr':lOdr,'mSpdFine':mSpdFine,'mSpd30MinCT':mSpd30MinCT,'mRest':mRest,'mRestMinutes':mRestMinutes,'mSleep30MinSD':mSleep30MinSD,'mSleep30MinCT':mSleep30MinCT})
		lmRasterPlot.extend(lmRasterPlot_temp)
		llOdr.append(lOdr)
		llStkName.append(lStkName)
		del mSpd, lStkName, lOdr, mRest, mRestMinutes, mSleep30MinSD, mSleep30MinCT, mSpdFine, mSpd30MinCT, nStk, lmRasterPlot_temp, lTerms
	
	# 生成睡眠光栅图
	drawRasterPlot(lmRasterPlot,outputDir)
	msg = '...睡眠光栅图绘制完毕\n'
	printReport(fReport, msg)
	del lmRasterPlot
	
	# 生成果蝇个体CT阶段标记文件 config_flys.txt
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
	msg = '...按变量类型分类保存数据\n'
	printReport(fReport, msg)
	isOk = saveSummaryData(outputDir)
	if not isOk:
		msg = '...数据整理步骤内存不足，请使用matlab脚本进行整理。\n'
		printReport(fReport, msg)
		return
	
	# 重新载入所需数据
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
	
	# 总结并汇报有效参数
	msg = '...\xca\xfd\xbe\xdd\xb7\xd6\xd7\xe9\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	msg = '...有效参数总结：\n'
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