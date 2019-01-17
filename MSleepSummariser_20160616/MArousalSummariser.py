import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import os

class ArousedStock(object):
    def __init__(self, cond='', stk='', lData=[]):
        self.cond = cond
        self.stk = stk
        self.data = np.array(lData) / 5  # convert 5-min data into per-min data
        self.mean = self.data.mean(axis=0)
        self.sem = self.data.std(axis=0) / np.sqrt(len(self.data))

    def getSummary(self):
        return '%s\t%s\t%f\t%f\t%d\n' \
               % (self.cond, self.stk, self.mean, self.sem, len(self.data))

    def __str__(self):
        return 'condition = %s; stock = %s; mean = %.5f; sem = %.5f; size = %d' \
               % (self.cond, self.stk, self.mean, self.sem, len(self.data))


def getItemList(lItems):
    lTypes = []
    for item in lItems:
        if item not in lTypes:
            lTypes.append(item)
    return lTypes


def parseInput(fInput):
    ## parse table info
    rawData = pd.read_csv(fInput, sep='\t', header=-1)
    lCond = getItemList(rawData[0])  # get condition list
    lStk = getItemList(rawData[1])  # get stock list
    ## parse table data
    lDiffStk = []
    lRtStk = []
    llMean = []
    llSem = []
    for cond in lCond:  # condition loop
        dfCond = rawData[rawData[0] == cond]  # data frame of a specific condition
        for stk in lStk:  # stock loop
            dfStk = dfCond[rawData[1] == stk]  # data frame of a specific stock
            lDiffStk.append(ArousedStock(cond, stk, dfStk[4]))  # save this stock
            lRtStk.append(ArousedStock(cond, stk, dfStk[5]))  # save this stock
            print '>>>>>> difference table'
            print lDiffStk[-1]
            print '>>>>>> ratio table'
            print lRtStk[-1]
            lMeanCurve = []
            lSemCurve = []
            for c in range(0,30):
                df = dfStk[7 + c]
                lMeanCurve.append(df.mean(axis=0))
                lSemCurve.append(df.std(axis=0) / math.sqrt(len(df)))
            llMean.append(lMeanCurve)
            llSem.append(lSemCurve)
    return lDiffStk, lRtStk, llMean, llSem


def printArousalIntensity(lStk, fOutput):
    hOut = open(fOutput, 'w')
    hOut.write('condition\tstock\tmean\tsem\tsize\n')
    for stk in lStk:
        hOut.write(stk.getSummary())
    hOut.close()


def printArousalCurve(lStk, llMean, llSem, dirOutput):
    lItems = []
    for stk in lStk:
        lItems.append(stk.stk)
    fOut = 'arousalcurve-summary.txt'
    fOut = os.path.join(dirOutput, fOut)
    hOut = open(fOut, 'w')
    for i, stk in enumerate(lStk):
        ## print mean data
        hOut.write('%s\t%s\tmean\t' % (stk.cond, stk.stk))
        for m in llMean[i]:
            hOut.write('%f\t' % m)
        hOut.write('\n')
        ## print sem data
        hOut.write('%s\t%s\tsem\t' % (stk.cond, stk.stk))
        for m in llSem[i]:
            hOut.write('%f\t' % m)
        hOut.write('\n')
    hOut.close()


dirRoot = 'D:/video/20160323_elav-Mesh1_arousal/arousalv4'
fInput = os.path.join(dirRoot, 'arousal_detal_v4.txt')
lDiffStk, lRtStk, llMeanCurve, llSemCurve = parseInput(fInput)
fOutDiff = os.path.join(dirRoot, 'arousal_intensity_v4.txt')
printArousalIntensity(lDiffStk, fOutDiff)
fOutRt = os.path.join(dirRoot, 'normal_activity_v4.txt')
printArousalIntensity(lRtStk, fOutRt)
printArousalCurve(lDiffStk, llMeanCurve, llSemCurve, dirRoot)
