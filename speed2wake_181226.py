from __future__ import print_function

import os
import sys
from joblib import Parallel, delayed
import multiprocessing as mp
import numpy as np

def getFileList(root_path, file_name):
	path_list = []
	for sub in os.listdir(root_path):
		if os.path.isdir(sub):
			subdir_path = os.path.join(root_path, sub)
			file_path = os.path.join(subdir_path, file_name)
			if os.path.exists(file_path):
				path_list.append(file_path)
	return path_list

def getSpeedFileList(root_path):
	return getFileList(root_path, 'txt.speed')

def getWakeFileList(root_path):
	return getFileList(root_path, 'txt.wake')

def getOrderFileList(root_path):
	return getFileList(root_path, 'txt.order')

def readWakeMat(wake_file):
	wake_mat = []
	with open(wake_file, 'r') as wake_h:
		for line in wake_h.readlines():
			terms = line.rstrip('\t\r\n').split('\t')
			if len(terms) < 1:
				continue
			val_list = [int(v) for v in terms]
			wake_mat.append(val_list)
	return np.array(wake_mat)

def getWakeMat(speed_file):
	wake_mat = []
	with open(speed_file, 'r') as speed_h:
		for line in speed_h.readlines():
			wake_mat.append([int(float(v) > 0) for v in line.rstrip('\t\r\n').split()])
	return np.array(wake_mat)

def saveWakeMat(wake_file, wake_mat):
	with open(wake_file, 'w') as wake_h:
		for line in wake_mat:
			for v in line:
				wake_h.write('%d\t' % v)
			wake_h.write('\n')

def singleSpeed2Wake(speed_file):
	print('get %s' % speed_file)
	wake_mat = getWakeMat(speed_file)
	wake_file = speed_file.rstrip('.speed')+'.wake'
	saveWakeMat(wake_file, wake_mat)

def runSpeed2Wake(root_path):
	cpu_num = mp.cpu_count()
	Parallel(n_jobs=cpu_num)(delayed(singleSpeed2Wake)(speed_file) for speed_file in getSpeedFileList(root_path))
	#for speed_file in getSpeedFileList(root_path):
		#print('converting file %s' % speed_file)
		#wake_mat = getWakeMat(speed_file)
		#wake_file = speed_file.rstrip('.speed')+'.wake'
		#saveWakeMat(wake_file, wake_mat)

def singleWake2Wake30(wake_file):
	wake30_mat = []
	print('get wake %s' % wake_file)
	wake_mat = readWakeMat(wake_file)
	tm_len = len(wake_mat)
	interval = 30*60
	for pt in range(0, tm_len, interval):
		margin = np.zeros((1,wake_mat.shape[1]))
		pt_end = min(pt + interval, tm_len)
		roi_mat = wake_mat[pt:pt_end, :]
		cpy_mat1 = np.concatenate([roi_mat, margin])
		cpy_mat2 = np.concatenate([margin, roi_mat])
		wake30_list = np.sum((cpy_mat2-cpy_mat1) < 0, axis=0)
		wake30_mat.append(wake30_list)
	wake30_file = wake_file.rstrip('.wake')+'.wake30'
	saveWakeMat(wake30_file, np.array(wake30_mat))

def runWake2Wake30(root_path):
	cpu_num = mp.cpu_count()
	Parallel(n_jobs=cpu_num)(delayed(singleWake2Wake30)(wake_file) for wake_file in getWakeFileList(root_path))
	#interval = 30*60
	#for wake_file in getWakeFileList(root_path):
		#wake30_mat = []
		#print('summarize wake-file %s' % wake_file)
		#wake_mat = readWakeMat(wake_file)
		#tm_len = len(wake_mat)
		#for pt in range(0, tm_len, interval):
			#margin = np.zeros((1,wake_mat.shape[1]))
			#pt_end = min(pt + interval, tm_len)
			#roi_mat = wake_mat[pt:pt_end, :]
			#cpy_mat1 = np.concatenate([roi_mat, margin])
			#cpy_mat2 = np.concatenate([margin, roi_mat])
			#wake30_list = np.sum((cpy_mat2-cpy_mat1) < 0, axis=0)
			#wake30_mat.append(wake30_list)
		#wake30_file = wake_file.rstrip('.wake')+'.wake30'
		#saveWakeMat(wake30_file, np.array(wake30_mat))

class MNamedExMat():
	def __init__(self, name):
		self.name = name
		self.mat = np.array([])
	
	def extend(self, add_mat, axis=0):
		add_rows, add_cols = add_mat.shape
		if len(self.mat) == 0:
			self.mat = add_mat
		else:
			my_rows, my_cols = self.mat.shape
			if axis == 0 and my_cols != add_cols:
				print('column dimension of adding matrix is invalid.')
				return
			elif axis == 1 and my_rows != add_rows:
				print('row dimension of adding matrix is invalid.')
				return
			elif axis > 1 or axis < 0:
				print('only 2D ExMat is supported.')
				return
			self.mat = np.concatenate([self.mat, add_mat], axis=axis)
	
	def __str__(self):
		return self.name
	
	def __eq__(self, other):
		return self.name == other.name

def divideMatByGroup(mat, group_dict, submat_dict={}, axis=1):
	for key, val in group_dict.items():
	#fly_idx_list = group_dict[which_group]
	#key = which_group
		if key in submat_dict.keys():
			if axis == 1:
				submat_dict[key].extend(mat[:, val])
			elif axis == 0:
				submat_dict[key].extend(mat[val])
			else:
				print('\t[divideMatByGroup]: currently only support axis=0 or axis=1')
				return
		else:
			exmat = MNamedExMat(key)
			if axis == 1:
				exmat.extend(mat[:, val])
			elif axis == 0:
				exmat.extend(mat[val, :])
			else:
				return
			submat_dict[key] = exmat
	return submat_dict

def getGroupDict(order_file):
	group_dict = {}
	with open(order_file, 'r') as order_h:
		for line in order_h.readlines():
			stk, order_list_s = line.rstrip('\t\r\n').split()
			order_list = [int(v) for v in order_list_s.split(',')]
			group_dict[stk.rstrip(':')] = order_list
	return group_dict

def getCfgFlyList(cfgfly_list_file):
	cfgfly_dict = {}
	with open(cfgfly_list_file, 'r') as cfg_h:
		for iL, line in enumerate(cfg_h.readlines()):
			if iL == 0:
				continue
			name, fly_idx, stage_list = line.rstrip(',\t\r\n').split()
			name = name.split('--')[1].rstrip(':')
			fly_idx = int(fly_idx) - 1
			if stage_list != 'none':
				stage_list = [int(v)-1 for v in stage_list.split(',')]
			else:
				stage_list = []
			if name not in cfgfly_dict.keys():
				cfgfly_dict[name] = [stage_list]
			else:
				cfgfly_dict[name].append(stage_list)
	return cfgfly_dict

def getCfgTmMat(cfgtm_file):
	cfgtm_mat = []
	with open(cfgtm_file, 'r') as cfgtm_h:
		for line in cfgtm_h.readlines():
			cfgtm_mat.append([int(v) for v in line.rstrip('\r\t\n').split()])
	cfgtm_mat = np.array(cfgtm_mat)
	cfgtm_mat[:, 0] -= 1
	return cfgtm_mat

def getCfgFlyDictPer30min(cfgtm_file, cfgfly_list_file):
	cfgfly_dict = getCfgFlyList(cfgfly_list_file)
	cfgtm_mat = getCfgTmMat(cfgtm_file)
	starttm_list = cfgtm_mat[:,0] / 30
	stoptm_list = cfgtm_mat[:,1] / 30
	for name, sect_mat in cfgfly_dict.items():
		tm_mat = []
		for sect_idxlist in sect_mat:
			if len(sect_idxlist) == 0:
				tm_mat.append([])
			else:
				start = sect_idxlist[0]
				stop = sect_idxlist[-1]
				start = starttm_list[start]
				stop = stoptm_list[stop]
				tm_mat.append([start, stop])
		cfgfly_dict[name] = tm_mat
	return cfgfly_dict

def printDict(name, dt):
	print('{{{{ <start>dict (%s)' % name)
	for k,v in dt.items():
		print('  %s -> ' % k, end='')
		print(v)
	print('}}}} <stop>dict (%s)' % name)

def getSectMat(curve_mat):
	interv = 24 # 0.5hr x 24
	num_30min = len(curve_mat[0])
	sect_mat = []
	for pt in range(0, num_30min, interv):
		sect_submat = np.sum(curve_mat[:, pt:min(pt + interv, num_30min)], axis=1)
		#sect_submat = sect_submat.reshape((1, len(curve_mat)))
		sect_mat.append(sect_submat)
	sect_mat = np.array(sect_mat)
	sect_mat = np.transpose(sect_mat)
	print(sect_mat.shape)
	return sect_mat

def saveFilteredWakeData(root_path, cfgfly_file):
	# enumerate every channel
	data_dict = {}
	for dir in os.listdir(root_path):
		dir_path = os.path.join(root_path, dir)
		if dir == '.' or dir == '..' or os.path.isfile(dir_path):
			continue
		# load order dictionary
		group_path = os.path.join(dir_path, 'txt.order')
		if os.path.exists(group_path):
			group_dict = getGroupDict(group_path)
		# load wake30 data matrix
		wake30_path = os.path.join(dir_path, 'txt.wake30')
		if not os.path.exists(wake30_path):
			continue
		wake30_mat = readWakeMat(wake30_path)
		# divide matrix into subgroup-dictionary
		data_dict = divideMatByGroup(wake30_mat, group_dict, data_dict)
		print('Loading channel %s data complete.' % dir)
		#printDict('data_dict', data_dict)
	# get cfgfly list
	cfgtm_file = os.path.join(root_path, 'config_time.txt')
	cfgfly_dict = getCfgFlyDictPer30min(cfgtm_file, cfgfly_file)
	# get dictionary of bounds list / filter list
	bounds_dict = {}
	filter_dict = {}
	for name, llCfg in cfgfly_dict.items():
		# check common lower/upper bounds of time range
		lower_bnd = sys.maxsize
		upper_bnd = -1
		for rg in llCfg:
			if len(rg) == 0:
				continue
			lb, ub = rg
			if lb < lower_bnd:
				lower_bnd = lb
			if upper_bnd < ub:
				upper_bnd = ub
		bounds_dict[name] = (lower_bnd, upper_bnd)
		# valid index list
		valid_idx_list = []
		for i, rg in enumerate(llCfg):
			if len(rg) > 0 and rg[0] == lower_bnd and rg[1] == upper_bnd:
				valid_idx_list.append(i)
		filter_dict[name] = valid_idx_list
	# save filtered data
	sum_mat_file = os.path.join(root_path, 'summary_matrix_wake-section.txt')
	sum_stat_file = os.path.join(root_path, 'summary_statistics_wake30.txt')
	sum_mat_h = open(sum_mat_file, 'w')
	sum_stat_h = open(sum_stat_file, 'w')
	for name, exmat in data_dict.items():
		# filter data: one vlaid fly per each line
		if name not in cfgfly_dict.keys():
			print('\t[warning] %s not in fly configuration dictionary.' % name)
			continue
		lb, ub = bounds_dict[name]
		fly_idx_list = filter_dict[name]
		curve_mat = np.transpose(exmat.mat)[fly_idx_list, lb:ub]
		mean_list = np.average(curve_mat, axis=0)
		sem_list = np.std(curve_mat, axis=0) / np.sqrt(len(curve_mat))
		# save individual data
		for fly_idx, wake_sect_list in enumerate(getSectMat(curve_mat)):
			sum_mat_h.write(name)
			for val in wake_sect_list:
				sum_mat_h.write('\t%d' % val)
			sum_mat_h.write('\n')
		# save stat data
		sum_stat_h.write('mean\t%d\t%s' % (len(curve_mat), name))
		for v in mean_list:
			sum_stat_h.write('\t%d' % v)
		sum_stat_h.write('\n')
		sum_stat_h.write('sem\t%d\t%s' % (len(curve_mat), name))
		for v in sem_list:
			sum_stat_h.write('\t%d' % v)
		sum_stat_h.write('\n')
	# close and save
	sum_mat_h.close()
	sum_stat_h.close()

def getCfgFlyPath(root_path):
	for root, sub, f in os.walk(root_path):
		if 'config_flys.txt' in f:
			return os.path.join(root, 'config_flys.txt')
	return None

def runApp(root_path = '.'):
	cfgfly_file = getCfgFlyPath(root_path)
	print(cfgfly_file)
	saveFilteredWakeData(root_path, cfgfly_file)

#runSpeed2Wake('.')
#runWake2Wake30('.')
runApp()