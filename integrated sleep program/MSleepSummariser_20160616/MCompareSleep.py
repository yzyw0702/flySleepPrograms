import os

from MCreateFlyStock import *
import matplotlib.pyplot as pl

def drawDistanceMap():
    pass


def compareSdWith(fsBefore, rSelBefore, fsAfter, rSelAfter):
    """
    compute info about the effects of sleep-deprivation (in brief, SD);
    accumulative sleep curve: (ptAfterSleep - ptBeforeSleep) / sum(ptBeforeNightSleep)
    :param fsBefore: <FlyStock>, sleep data before SD
    :param rSelBefore: <2-element List>, range (hr) of a whole day selected from [fsBefore], in the order of day -> night
    :param fsAfter: <FlyStock>, sleep data after SD
    :param rSelAfter: <2-element List>, range (hr) of a whole day selected from [fsAfter], in the order of day -> night
    :returns lAvgAcc, lSemAcc: <Matrix>, n30min, n30min
    """
    # check data validity
    assert isinstance(fsBefore, FlyStock)
    assert isinstance(fsAfter, FlyStock)
    ## get sleep level of night-section before SD
    nSection, lAvgSlpSect, lSemSlpSect, matSlpSect = fsBefore.getSectionData()
    slpDeprived = lAvgSlpSect[int(rSelBefore[-1]/ 12) - 1]  # get level of sleep deprived
    n30min = int(rSelAfter[-1] * 2 - rSelAfter[0] * 2)  # compute duration in minutes
    if int(rSelBefore[-1] * 2 - rSelBefore[0] * 2) != n30min:
        return None, None
    ## compute point-point difference between after-SD - before-SD, in the order of [day night]
    matDiffSlp30 = []  # matrix of 30-min sleep difference for each fly
    for iA, idxAfter in enumerate(fsAfter.lIdxFly):
        lAfter = fsAfter.matDataRaw[iA][int(rSelAfter[0]) * 2:int(rSelAfter[-1]) * 2]  # get a fly after SD
        iB = fsBefore.getIdxRowWith(idxAfter)
        if iB == -1:  # jump fly that not exists in flystock before SD
            continue
        lBefore = fsBefore.matDataRaw[iB][int(rSelBefore[0]) * 2:int(rSelBefore[-1]) * 2]  # get a corresponding fly before SD
        lDiff = []
        for i in range(n30min):
            lDiff.append((lAfter[i] - lBefore[i]) / slpDeprived)
        matDiffSlp30.append(lDiff)
    # compute average and S.E.M. of difference
    lSumDiff = []
    for i in range(n30min):
        lSumDiff.append(0.0)
    for i, lD in enumerate(matDiffSlp30):
        for j, d in enumerate(lD):
            lSumDiff[j] += d
    lAvgDiff = []
    for i in range(n30min):
        lAvgDiff.append(lSumDiff[i] / len(matDiffSlp30))
    lAvgAcc = []
    acc = 0
    for i in range(n30min):
        acc += lAvgDiff[i]
        lAvgAcc.append(acc)
    lSemAcc = []
    for i in range(n30min):
        lSemAcc.append(0.0)
    lAcc = []
    for iF in range(len(matDiffSlp30)):
        lAcc.append(0.0)
    for iF, lD in enumerate(matDiffSlp30):
        for t, d in enumerate(lD):
            lAcc[iF] += d
            lSemAcc[t] += (lAcc[iF] - lAvgAcc[t]) ** 2
    for i in range(n30min):
        lSemAcc[i] = math.sqrt(lSemAcc[i]) / len(matDiffSlp30)
    return lAvgAcc, lSemAcc, matDiffSlp30


def drawSdAccumulativeCurveWith(lFsBefore, rSelBefore, lFsAfter, rSelAfter, fig, outDir=None, lColors='bgrcmk'):
    ax = fig.add_subplot(111)
    lTime = lFsAfter[0].lTime[0:int(rSelAfter[-1] * 2 - rSelAfter[0] * 2)]
    lPlots = []
    lNameCb = []
    pathOut = os.path.join(outDir, 'accumulative_difference.txt')
    pathSum = os.path.join(outDir, 'accumulative_mean-sem.txt')
    fid = open(pathOut, 'w')
    fidSum = open(pathSum, 'w')
    for i, fsBefore in enumerate(lFsBefore):
        fsAfter = lFsAfter[i]
        assert isinstance(fsAfter, FlyStock)
        lAccDiff, lSemAcc, matDiffSlp30 = compareSdWith(fsBefore, rSelBefore, fsAfter, rSelAfter)

        fid.write('stock: %s\n' % fsAfter.name)
        for iF, lD in enumerate(matDiffSlp30):
            for t, d in enumerate(lD):
                fid.write('%f\t' % d)
            fid.write('\n')

        fidSum.write('stock: %s\n' % fsAfter.name)
        fidSum.write('mean:\t')
        for v in lAccDiff:
            fidSum.write('%f\t' % v)
        fidSum.write('\n')
        fidSum.write('sem:\t')
        for v in lSemAcc:
            fidSum.write('%f\t' % v)
        fidSum.write('\n')

        if not lAccDiff:
            print 'in valid SD-data from stock <%s>.' % fsAfter.name
            continue
        ax.plot(lTime, lAccDiff, picker=True, label=fsAfter.name)
        oneplot = ax.errorbar(lTime, lAccDiff, yerr=lSemAcc, label=fsAfter.name, color=lColors[i%6])
        lNameCb.append(fsAfter.name)
        lPlots.append(oneplot)
    fid.close()
    fidSum.close()
    pl.title('accumulative curve of rebound sleep after deprivation')
    pl.legend(lPlots, lNameCb, loc='best')
    pl.xlabel('time (unit: hour)')
    pl.ylabel('recovery ratio')
    pl.ylim(-0.4, 0.2)


def getCommonList(llInput):
    # find the shortest list
    iMinList = 0
    minLen = llInput[0]
    for i,l in enumerate(llInput):
        if minLen > len(l):
            minLen = len(l)
            iMinList = i
    # get indices of other lists
    lIdxRest = range(len(llInput))
    lIdxRest.remove(iMinList)
    # check shortest common list
    lCommon = []
    for e in llInput[iMinList]:
        isExist = True
        for iL in lIdxRest:
            isExist *= (e in llInput[iL])
        if isExist:
            lCommon.append(e)
    return lCommon


def compareVortexWith(fStock, rSelBefore, rSelDuring, rSelAfter):
    """
    compute info about the effects of sleep-deprivation (in brief, SD);
    accumulative sleep curve: (ptAfterSleep - ptBeforeSleep) / sum(ptBeforeNightSleep)
    :param fStock: <FlyStock>, sleep data, including before/during/after
    :param rSelBefore: <2-element List>, range (hr) of a whole day selected as before section, in the order of day -> night
    :param rSelDuring: <2-element List>, range (hr) of a whole day selected as during section, in the order of day -> night
    :param rSelAfter: <2-element List>, range (hr) of a whole day selected as after section, in the order of day -> night
    :returns lFlyIdx, lRatioDeprived, llReboundAcc: <nFly List>, <nFly List>, <nFly x n30min 2D List>
    """
    # check data validity
    assert isinstance(fStock, FlyStock)
    assert rSelBefore[-1] - rSelBefore[0] == 24
    assert rSelDuring[-1] - rSelDuring[0] == 12
    assert rSelAfter[-1] - rSelAfter[0] == 24
    ## get level of night-section before SD
    n30min = 24 * 2  # compute duration in 30-minutes
    # get section level
    nSect, lAvgSect, lSemSect, matSect = fStock.getSectionData()
    # compute deprived sleep and its ratio
    lSlpDeprived = []  # <nFly List>
    lRatioDeprived = []  # <nFly List>
    lRowIdx = []  # fly indices in matSect
    lFlyIdx = []  # fly indices in reality
    for iF, lSect in enumerate(matSect):
        slpBefore = lSect[int(rSelBefore[-1] / 12) - 1]
        if slpBefore == 0:  # remove fly of no baseline sleep
            continue
        slpDuring = lSect[int(rSelDuring[-1] / 12) - 1]
        lRowIdx.append(iF)
        lFlyIdx.append(fStock.lIdxFly[iF])
        slpDeprived = slpBefore - slpDuring
        lSlpDeprived.append(slpDeprived)
        lRatioDeprived.append(slpDeprived / slpBefore)
    ## compute point-point difference between after-SD - before-SD, in the order of [day night]
    llDiffSlp30 = []  # matrix of 30-min sleep difference for each fly
    for iF in lRowIdx:
        lAfter = fStock.matDataRaw[iF][int(rSelAfter[0]) * 2:int(rSelAfter[-1]) * 2]  # get a fly after SD
        lBefore = fStock.matDataRaw[iF][int(rSelBefore[0]) * 2:int(rSelBefore[-1]) * 2]  # get a corresponding fly before SD
        lDiff = []
        for i in range(n30min):
            lDiff.append((lAfter[i] - lBefore[i]) / lSlpDeprived[iF])
        llDiffSlp30.append(lDiff)
    # compute accumulative differences over all flies
    llReboundAcc = []  # <nFly x n30min 2d-List>
    for i, lDiff in enumerate(llDiffSlp30):
        acc = 0
        llReboundAcc.append([])
        for d in lDiff:
            acc += d
            llReboundAcc[-1].append(acc)
    return lFlyIdx, lRatioDeprived, llReboundAcc


def printVortexAccumulativeDiffWith(lFStocks, rSelBefore, rSelDuring, rSelAfter, outDir):
    for i, fStock in enumerate(lFStocks):
        assert isinstance(fStock, FlyStock)
        lFlyIdx, lRatioDeprived, llReboundAcc = compareVortexWith(fStock, rSelBefore, rSelDuring, rSelAfter)
        pathOut = os.path.join(outDir, fStock.name + '_accumulative-curve.txt')
        fid = open(pathOut, 'w')
        # write head line
        fid.write('index\tdeprived_ratio\trebound_curve (in 30 mins)...\n')
        # write data
        for iF, lD in enumerate(llReboundAcc):
            fid.write('%d\t%f\t' % (lFlyIdx[iF], lRatioDeprived[iF]))
            for d in lD:
                fid.write('%f\t' % d)
            fid.write('\n')
        fid.close()


def testDrawSdAccumulativeCurve():
    fBefore = 'H:/video/2018-1/20180422_SISL-isoCS_M1KO_male/matlab/before/sleep_30mins_CT.txt'
    fAfter = 'H:/video/2018-1/20180422_SISL-isoCS_M1KO_male/matlab/after/sleep_30mins_CT.txt'
    fOutput = 'D:/video/201660519_SISL_rescue-line_male/stv/summary'
    rSelBefore = [12, 24]
    rSelAfter = [0, 12]
    dFsBefore = createFlyStocksWith(fBefore)
    dFsAfter = createFlyStocksWith(fAfter)
    fig = pl.figure()
    drawSdAccumulativeCurveWith(dFsBefore.values(), rSelBefore, dFsAfter.values(), rSelAfter, fig, fOutput)
    pl.show()


def testPrintVortexAccumulativeCurve():
    fInput = 'D:/video/20151203_Mesh1KO_vortexSD/matlab/raw/sleep_30mins_CT.txt'
    fOutput = 'D:/video/20151203_Mesh1KO_vortexSD/matlab/raw/summary'
    rSelBefore = [48, 72]
    rSelDuring = [84, 96]
    rSelAfter = [96, 120]
    dFs = createFlyStocksWith(fInput)
    printVortexAccumulativeDiffWith(dFs.values(), rSelBefore, rSelDuring, rSelAfter, fOutput)


# testPrintVortexAccumulativeCurve()
testDrawSdAccumulativeCurve()
