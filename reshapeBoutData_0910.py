import pandas as pd
import numpy as np
import os


def reshapeBoutData(fIn, fOutPrefix):
	df = pd.read_table(fIn)
	df.fillna(-1)
	lName = list(df['name'])
	lName = sorted(set(lName), key=lName.index)
	lTerms = df.columns[2:]
	mStat = []
	#lFSubOut = []
	for iTerm, term in enumerate(lTerms):  # separately save different properties into distinct output files
		fSubOut = fOutPrefix + term + '.txt'
		#lFSubOut.append(fSubOut)
		h = open(fSubOut, 'w')
		h.write('%s\t' % term)
		llVal = []
		for name in lName:
			h.write('%s\t' % name)
			llVal.append(list(df[df['name']==name][term]))
		h.write('\n')
		lN = []
		llCorrVal = []
		for lVal in llVal:  # list of number for each group
			nVal = 0
			lCorrVal = []
			for v in lVal:
				if v >= 0:
					nVal +=1
					lCorrVal.append(v)
			lN.append(nVal)
			llCorrVal.append(lCorrVal)
		if iTerm == 0:
			mStat.append(lN)
		for iRow in range(np.max(lN)):
			h.write('\t')
			for iList, lCorrVal in enumerate(llCorrVal):
				if iRow < lN[iList]:
					h.write('%.3f\t' % lCorrVal[iRow])
				else:
					h.write('\t')
			h.write('\n')
		# write statistics
		for name in lName:
			h.write('\t%s' % name)
		h.write('\n')
		h.write('mean\t')
		mStat.append([])
		for lCorrVal in llCorrVal:
			avg = np.mean(np.array(lCorrVal))
			mStat[-1].append(avg)
			h.write('%.3f\t' % avg)
		h.write('\n')
		h.write('sem\t')
		lSqrtN = np.sqrt(lN)
		mStat.append([])
		for i, lCorrVal in enumerate(llCorrVal):
			sem = np.std(np.array(lCorrVal)) / lSqrtN[i]
			mStat[-1].append(sem)
			h.write('%f\t' % (sem))
		h.write('\n')
		h.write('N\t')
		for n in lN:
			h.write('%d\t' % n)
		h.write('\n')
		h.close()
	mStat = np.array(mStat).T
	
	# save summary file
	fSummary = fOutPrefix + '-summary.txt'
	hSummary = open(fSummary, 'w')
	# write title
	hSummary.write('stock_name\tsample_number')
	for term in lTerms:
		hSummary.write('\t%s_mean\t%s_sem' % (term, term))
	hSummary.write('\n')
	# write data
	for r, name in enumerate(lName):
		hSummary.write(name)
		for c in range(len(lTerms)*2 + 1):
			hSummary.write('\t%f' % mStat[r, c])
		hSummary.write('\n')
	hSummary.close()


def reshapeOneFile(fInput):
	fOutPrefix = fInput[:-4] + '-'
	reshapeBoutData(fInput, fOutPrefix)


def batchReshape(rootpath):
	for f in os.listdir(rootpath):
		if os.path.isdir(f) or not '.txt' in f:
			continue
		reshapeOneFile(f)


reshapeOneFile('./sleepEpisode_clean.txt')