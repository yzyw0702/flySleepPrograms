# coding=utf-8
import numpy as np
import time as tm
import uniout
import cv2
import copy
import scipy.io as sio
from myutils import *

def F_main_SD_R(dirPath=None,outputDir=None):
	#主入口，20140407-09全部重编码
	
	#使用的阈值为连续5mins speed=0记录为sleep,中间允许任何数目的<=2frames(2secs)的连续speed不为0的缺口
#首先必须满足两侧的连续不懂的时长都满足>=5mins之后才考虑去除噪音点
#默认分析从第一个点开始的所有数目,如果需要修改，请处理的时候调整开始处理的时间
	
	#如果需要屏蔽某一个文件的结果，请暂时将该文件中的txt.speed的扩展名修改为别的东西，则程序忽略该文件以及关联的.location以及.order
	
	#为了正确的计算距离食物的位置，录像需要满足一下条件：1,食物在板子的中间; 2,所有的管子都为平行或者垂直排列; 3,每一个板子的左右都必须至少有一个可以使用的管子
	
	#输出文件有raw plot.jpeg; config_flys.txt用于校正死亡的果蝇, report.txt记录程序运行报告,
#'time'_main_SD_R_imported_speed.mat记录输入的.speed数据合集;
#'time'_main_SD_R_imported_location.mat记录输入的.location数据合集
#'time'_main_SD_R.mat记录输入的.order数据,以及中间计算的变量，具体见最后一个cell的说明

	# create output directory
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)
	# set report file
	fReport = os.path.join(outputDir,'report.txt')
	# log i/o info
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
	# set input dataset
	lFSpd=getAllFiles(dirPath,'txt.speed') # speed dataset
	#locationList=[f[:-9] + 'txt.location' for f in lFSpd]
	lFOdr=[f[:-9] + 'txt.order' for f in lFSpd] # order lists
	
	#录入时间信息,生成mTime记录时间顺序
	fCfgTime=os.path.join(dirPath,'config_time.txt')
	mTime=readTime(fCfgTime,fReport)
	if len(mTime) == 0: # stop program if mTime is invalid
		msg = '...config_time.txt 设置不正确。\n'
	else:
		msg = '...config_time.txt 正常加载\n'
	printReport(fReport, msg)
	
	#录入所有的.speed和.order文件
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
			msg = '......txt.speed 文件 %s 总时长 (%d sec) 比 config_time.txt 中设置的总时间 (%d sec) 短。\n' % (fSpd[:-9], nTmSpd, nTmCfg)
			printReport(fReport, msg)
			return False
		msg = '......' + fSpd
		printReport(fReport, msg)
		msg = ' 导入完成。矩阵尺寸 %d x %d\n'  % (nTmSpd, nFlySpd)
		printReport(fReport, msg)
		msg = '......txt.order 导入完成：'
		printReport(fReport, msg)
		msg = printOdrTable(lStkName, lOdr)
		# msg += headOf(lmSpd[-1], 2, 'data-matrix-%d' % i)
		printReport(fReport, msg)
	
	# 计算最短时长
	# lTotalTmSpd_tmp记录速度文件总时长 (单位：min)
	lTotalTmSpd_tmp = [np.floor(len(mSpd) / 60) for mSpd in lmSpd]
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

	# 计算休息矩阵：判断每一秒钟内果蝇是运动还是休息
	lenBout = 5 * 60 # 以5分钟作为一个睡眠事件的基本单元
	#对每个速度矩阵进行降噪
	lmRest=[] # 休息矩阵列表，尺寸为 nChannel x nTime x nFly；1代表不动，0代表运动
	kernelTm=cv2.getStructuringElement(cv2.MORPH_RECT,(1, lenBout)) # 第2个参数为结构元素的尺寸，1和lenBout依次是宽和高，即每5分钟一个单元进行平滑处理
	for i, mSpd in enumerate(lmSpd):
		mSleep_tmp=np.zeros(np.shape(mSpd)) # 休息矩阵初始化
		mSleep_tmp[mSpd <= 0]=1 # 找到果蝇不动的时刻
		mSleep_tmp = cv2.morphologyEx(mSleep_tmp, cv2.MORPH_OPEN, kernelTm)
		lmRest.append(mSleep_tmp)
	#批量判定睡眠时间之前，先判断一下视频末尾的最后五分钟内，果蝇是否在睡
	for iChn, mRest in enumerate(lmRest): # 对于每一个录像通道
		nFly = len(mRest[0]) # 当前通道的果蝇个数
		for iFly in range(nFly): # 对于每一只果蝇
			if mRest[-1,iFly] == 1: # 只针对末尾处于睡眠的情况
				infoWakeTm = np.where(mRest[:, iFly] == 0) # 找到运动的时刻
				lWakeTm = infoWakeTm[0]
				# 最后5分钟内只要该果蝇清醒过一次，
				if len(lWakeTm) > 0 and len(mRest) - lWakeTm[-1] < lenBout:
					lmRest[iChn][lWakeTm[-1]:, iFly] = 0 # 就记作清醒事件
	msg = '...果蝇休息数据计算完毕\n'
	printReport(fReport, msg)
	
	#获得每分钟休息时长,lmRestMinutes, 60个点的数据合并;
	lmRestMinutes=[] # 每分钟休息矩阵列表，尺寸为 nChannel x nTime/60 x nFly；>0代表休息时长（单位：秒）
	for iChn, mRest in enumerate(lmRest):
		nFly = len(mRest[0]) # 当前通道的果蝇个数
		mRestMinutes=np.zeros((minTotalTm, nFly))
		# sum up data of 60 seconds into that of 1 min
		for iM in range(minTotalTm-1):
			mRestMinutes[iM]=np.sum(mRest[iM*60:(iM+1)*60],axis=0)
		lmRestMinutes.append(mRestMinutes)
	msg = '...果蝇每分钟休息数据计算完毕\n'
	printReport(fReport, msg)

	#计算每30mins的睡眠时长，分别按照CT时间划分30mins(normal sleep 分析)以及按照录像开始每30mins划分(SD sleep rebount)
	#lmSleep30MinSD: max calculated length 24hours
	lmSleep30MinSD=[] # 每半小时的睡眠矩阵列表，尺寸为 nChannel x nTime/1800 x nFly；>0代表睡眠时长（单位：秒）
	lenSleep30MinSD = 48 # SD后最关注的是第1天的睡眠数据（24小时，共48个点）
	if minTotalTm < 1440: # 如果视频全长小于24小时
		lenSleep30MinSD = np.floor(minTotalTm / 30)
	for iChn, mRestMinutes in enumerate(lmRestMinutes):
		nFly = len(mRestMinutes[0]) # 当前通道的果蝇个数
		mSleep30MinSD=np.zeros((lenSleep30MinSD, nFly))
		for iHalf in range(lenSleep30MinSD):
			mSleep30MinSD[iHalf]=np.sum(mRestMinutes[iHalf*30:(iHalf+1)*30],axis=0)
		lmSleep30MinSD.append(mSleep30MinSD)
	msg = '...果蝇每半小时睡眠数据（SD版本）计算完毕\n'
	printReport(fReport, msg)
	
	# 计算总共存在几个白天
	nDaysCT = 1 
	if mTime[0,2] == 0: # 如果第一个阶段是夜晚
		nDaysCT += np.ceil((len(mTime) - 1.0) / 2.0)
	else: # 如果第一个阶段是白天
		nDaysCT += np.ceil((len(mTime) - 2.0) / 2.0)
	nDaysCT = int(nDaysCT)
	#lmSleep30MinCT,按照CT计算每半小时的睡眠水平，第一段时间如果<30mins，将自动忽略
	lmSleep30MinCT=[]
	for iChn, mRestMinutes in enumerate(lmRestMinutes):
		nFly = len(mRestMinutes[0]) # 当前通道的果蝇个数
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
		lmSleep30MinCT.append(mSleep30MinCT)
	msg = '...果蝇每半小时睡眠数据（CT版本）计算完毕\n'
	printReport(fReport, msg)
	
	#可用的数据有 lmRest(判断每一秒是否处于睡眠); lmRestMinutes为每一分钟睡眠数据，需用于生成jpeg raw sleep图
#lmSleep30MinSD 按照录像开始每30mins划分(SD sleep rebount),  lmSleep30MinCT 按照CT时间划分30mins(normal sleep 分析)
## 处理.speed 数据，分析运动速度,依据每分钟合并，以及每30mins合并
# ！speed 数据经过降噪，因为trace可能暂时跟丢，将计算一个超大的数值，本处暂时忽略所有speed>=10 的 point！
	lmSpdFine=[] # 降噪后的速度矩阵列表，尺寸为 nChannel x nTime x nFly
	for iChn, mSpd in enumerate(lmSpd):
		mSpdFine=mSpd
		mSpdFine[0][mSpd[0] == 1] = - 1 # 把初始速度等于1的值都改标记为-1
		mSpdFine[mSpdFine >= 10] = - 2 # 把速度大于10的地方都标为-2
		lmSpdFine.append(mSpdFine)
	msg = '...降噪后的果蝇速度数据计算完毕\n'
	printReport(fReport, msg)
	#依据CT time计算30mins之类speed的平均值
	lmSpd30MinCT=[] # 30分钟速度矩阵列表（CT版本），尺寸为 nChannel x nTime x nFly
	for iChn, mSpdFine in enumerate(lmSpdFine):
		nFly = len(mSpdFine[0])
		mSpdMove = copy.deepcopy(mSpdFine) # 降噪后的每秒速度矩阵
		mSpdMove[mSpdFine < 0] = 0 # 将速度小于零的地方标记为 0
		mTimeMove = np.zeros(np.shape(mSpdMove)) # 运动状态的时间分布矩阵
		mTimeMove[mSpdFine >= 0] = 1 # 将处于运动状态的地方标记为1
		mSpd30MinCT = np.zeros(np.shape(lmSleep30MinCT[iChn])) - 1 # 空缺位置标记为 -1
		tSpd = int(np.ceil(mCtTm[0,1] / 30))
		lSumSpdMove = np.zeros((1,nFly))
		lNTmMove = np.zeros((1,nFly))
		for t in range(minTotalTm*60):
			lSumSpdMove += mSpdMove[t,:] # 累加运动距离
			lNTmMove += mTimeMove[t,:] # 累加运动时长
			if mCtTm[int(np.ceil(t / 60)),1] % 30 == 0 and t%60 == 0: # 每30分钟记录一次数据
				for iFly, distance in enumerate(lSumSpdMove[0]):
					if lNTmMove[0,iFly] > 0:
						mSpd30MinCT[tSpd,iFly]=lSumSpdMove[0,iFly] / lNTmMove[0,iFly]
					else:
						mSpd30MinCT[tSpd,iFly] = -1
				tSpd += 1
				lSumSpdMove = np.zeros((1,nFly))
				lNTmMove = np.zeros((1,nFly))
		tSpd = int(np.ceil(mCtTm[0,1] / 30))
		if not (mCtTm[0,1] - 1) % 30 == 0: # 如果第一段时间不足30分钟，则去除
			mSpd30MinCT[tSpd] = -1
		lmSpd30MinCT.append(mSpd30MinCT)
		msg = '......第 %d 个文件的30Min运动速度数据（CT版本）计算完毕。\n' % (iChn+1)
		printReport(fReport,msg)
	# 保存导入的速度数据
	fOutSpd = os.path.join(outputDir,'main-py_SD_R_imported_speed.mat')
	sio.savemat(fOutSpd, {'lmSpd': lmSpd})
	# return True

	# 生成睡眠光栅图
	nStk=0 # 计数品系数目,nStk
	lmRasterPlot = []
	for iChn in range(len(lFSpd)):
		nStk += len(llOdr[iChn])
		lmRasterPlot_temp=[]
		for iStk, lIdx in enumerate(llOdr[iChn]):
			lmRasterPlot_temp.append([])
			mRasterPlot = np.zeros((len(mCtTm),len(lIdx) + 1))
			mRasterPlot[:, 0] = mCtTm[:, 0] # 第一列是光照条件（白天=1，黑夜=0）
			lIdx = np.array(lIdx)
			mRasterPlot[:, 1:] = lmRestMinutes[iChn][:, lIdx - 1]
			lmRasterPlot_temp[-1].append(llStkName[iChn][iStk])
			lmRasterPlot_temp[-1].append(mRasterPlot)
		lmRasterPlot.extend(lmRasterPlot_temp)
	drawRasterPlot(lmRasterPlot,outputDir)
	msg = '...睡眠光栅图绘制完毕\n'
	printReport(fReport, msg)
	
	# 生成果蝇个体CT阶段标记文件 config_flys.txt
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

	# 总结并汇报有效参数
	msg = '...\xca\xfd\xbe\xdd\xb7\xd6\xd7\xe9\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	msg = '...有效参数总结：\n'
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

	# 保存有效参数
	fOutAll = os.path.join(outputDir,'main-py_SD_R.mat')
	sio.savemat(fOutAll, {'sourcePath':dirPath, 'mTime':mTime, 'mCtTm':mCtTm, 'minTotalTm':minTotalTm, 'llStkName':llStkName,'llOdr':llOdr,'lmSpdFine':lmSpdFine,'lmSpd30MinCT':lmSpd30MinCT,'lmRest':lmRest,'lmRestMinutes':lmRestMinutes,'lmSleep30MinSD':lmSleep30MinSD,'lmSleep30MinCT':lmSleep30MinCT})
	msg = '...\xca\xfd\xbe\xdd\xb1\xa3\xb4\xe6\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	
	msg='...\xb9\xd8\xb1\xd5\n'
	printReport(fReport, msg)
	return True

	


def F_onechannel_SD_R(dirChannel, iChn, mTime, mCtTm, minTotalTm, nDaysCT, lenSleep30MinSD, fReport):
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
	msg = '......' + fSpd
	printReport(fReport, msg)
	msg = ' 导入完成。矩阵尺寸 %d x %d\n'  % (nTmSpd, nFly)
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
	for iFly in range(nFly): # 对于每一只果蝇
		if mRest[-1,iFly] == 1: # 只针对末尾处于睡眠的情况
			infoWakeTm = np.where(mRest[:, iFly] == 0) # 找到运动的时刻
			lWakeTm = infoWakeTm[0]
			# 最后5分钟内只要该果蝇清醒过一次，
			if len(lWakeTm) > 0 and len(mRest) - lWakeTm[-1] < lenBout:
				mRest[lWakeTm[-1]:, iFly] = 0 # 就记作清醒事件
	msg = '......果蝇休息数据计算完毕\n'
	printReport(fReport, msg)
	
	#获得每分钟休息时长,mRestMinutes, 60个点的数据合并;
	mRestMinutes=np.zeros((minTotalTm, nFly)) # 每分钟休息矩阵，尺寸为 nTime/60 x nFly；>0代表休息时长（单位：秒）
	# sum up data of 60 seconds into that of 1 min
	for iM in range(minTotalTm-1):
		mRestMinutes[iM]=np.sum(mRest[iM*60:(iM+1)*60],axis=0)
	msg = '......果蝇每分钟休息数据计算完毕\n'
	printReport(fReport, msg)
	
	#计算每30mins的睡眠时长，分别按照CT时间划分30mins(normal sleep 分析)以及按照录像开始每30mins划分(SD sleep rebount)
	nFly = len(mRestMinutes[0]) # 当前通道的果蝇个数
	mSleep30MinSD=np.zeros((lenSleep30MinSD, nFly))
	for iHalf in range(lenSleep30MinSD):
		mSleep30MinSD[iHalf]=np.sum(mRestMinutes[iHalf*30:(iHalf+1)*30],axis=0)
	msg = '......果蝇每半小时睡眠数据（SD版本）计算完毕\n'
	printReport(fReport, msg)
	
	#mSleep30MinCT,按照CT计算每半小时的睡眠水平，第一段时间如果<30mins，将自动忽略
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
	msg = '......果蝇每半小时睡眠数据（CT版本）计算完毕\n'
	printReport(fReport, msg)
	
	# 速度数据降噪
	mSpdFine = copy.deepcopy(mSpd) # 降噪后的速度矩阵列表，尺寸为 nTime x nFly
	mSpdFine[0][mSpd[0] == 1] = - 1 # 把初始速度等于1的值都改标记为-1
	mSpdFine[mSpdFine >= 10] = - 2 # 把速度大于10的地方都标为-2
	msg = '......降噪后的果蝇速度数据计算完毕\n'
	printReport(fReport, msg)
	
	#依据CT time计算30mins speed的平均值
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
	msg = '......30Min运动速度数据（CT版本）计算完毕。\n'
	printReport(fReport,msg)
	
	# 生成睡眠光栅图子表
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
	msg = '......睡眠光栅图子表生成完毕\n'
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
	
	#lmSleep30MinSD: 设定SD版本数据的总时长
	lenSleep30MinSD = 48 # SD后最关注的是第1天的睡眠数据（24小时，共48个点）
	if minTotalTm < 1440: # 如果视频全长小于24小时
		lenSleep30MinSD = np.floor(minTotalTm / 30)
	
	# 分录像通道分析睡眠数据
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
	
	# 保存导入的速度数据
	fOutSpd = os.path.join(outputDir,'main-py_SD_R_imported_speed.mat')
	sio.savemat(fOutSpd, {'lmSpd': lmSpd})
	
	# 生成睡眠光栅图
	drawRasterPlot(lmRasterPlot,outputDir)
	msg = '...睡眠光栅图绘制完毕\n'
	printReport(fReport, msg)
	
	# 生成果蝇个体CT阶段标记文件 config_flys.txt
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
	
	# 总结并汇报有效参数
	msg = '...\xca\xfd\xbe\xdd\xb7\xd6\xd7\xe9\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	msg = '...有效参数总结：\n'
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

	# 保存有效参数
	fOutAll = os.path.join(outputDir,'main-py_SD_R.mat')
	sio.savemat(fOutAll, {'sourcePath':dirPath, 'mTime':mTime, 'mCtTm':mCtTm, 'minTotalTm':minTotalTm, 'llStkName':llStkName,'llOdr':llOdr,'lmSpdFine':lmSpdFine,'lmSpd30MinCT':lmSpd30MinCT,'lmRest':lmRest,'lmRestMinutes':lmRestMinutes,'lmSleep30MinSD':lmSleep30MinSD,'lmSleep30MinCT':lmSleep30MinCT})
	msg = '...\xca\xfd\xbe\xdd\xb1\xa3\xb4\xe6\xcd\xea\xb1\xcf\n'
	printReport(fReport, msg)
	
	msg='...\xb9\xd8\xb1\xd5\n'
	printReport(fReport, msg)
	return True
	
	