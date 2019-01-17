import os

import matplotlib.pyplot as pl
import numpy as np
from MCreateFlyStock import *


def drawSleepRawCurveWith(lFStock, fig, rSelected=None, lColors='bgrcmk'):  # draw sleep (per unit time) curves for FlyStock list [lFStock]
    assert isinstance(lFStock, list)
    pl.style.use('bmh')
    ax = fig.add_subplot(111)
    ax.set_title('click on line to get its stock name')
    lPlots = []
    lNameCb = []
    for i, stk in enumerate(lFStock):
        assert isinstance(stk, FlyStock)
        if not rSelected:
            lTime = stk.lTime[:]
            lData = stk.lAvgDataRaw[:]
            lSem = stk.lSemDataRaw[:]
        else:
            lTime = stk.lTime[int(rSelected[0] * 2):int(rSelected[-1] * 2)]
            lData = stk.lAvgDataRaw[int(rSelected[0] * 2):int(rSelected[-1] * 2)]
            lSem = stk.lSemDataRaw[int(rSelected[0] * 2):int(rSelected[-1] * 2)]
        ax.plot(lTime, lData, picker=True, label=stk.name)
        oneplot = ax.errorbar(lTime, lData, yerr=lSem, color=lColors[i])
        lNameCb.append(stk.name)
        lPlots.append(oneplot)
    pl.title('sleep curve on 30-min')
    pl.legend(lPlots, lNameCb, loc='best')
    pl.xlabel('time (unit: hour)')
    pl.ylabel('sleep level (unit: seconds)')
    pl.ylim(0, 1800)


def drawSleepSectCurveWith(lFStock, fig, rSelected=None, lColors='bgrcmk'):  # draw sleep (per 12-hour) bars for FlyStock list [lFStock]
    assert isinstance(lFStock, list)
    pl.style.use('bmh')
    lPlots = []
    lNameCb = []
    wBars = .6 / len(lFStock)
    ax = fig.add_subplot(111)
    for i, stk in enumerate(lFStock):
        assert isinstance(stk, FlyStock)
        nSection, lAvgSlpSect, lSemSlpSect, matSlpSect = stk.getSectionData()
        idxBars = np.arange(nSection)  # by default, draw all sections
        if not rSelected:
            lData = lAvgSlpSect[:]
            lSem = lSemSlpSect[:]
        else:
            idxBars = np.arange(int(rSelected[-1] - rSelected[0]) / 12)
            lData = lAvgSlpSect[int(rSelected[0] / 12):int(rSelected[-1] / 12)]
            lSem = lSemSlpSect[int(rSelected[0] / 12):int(rSelected[-1] / 12)]
        lPlots.append( ax.bar(idxBars + i * wBars, lData, wBars, yerr=lSem, color=lColors[i], label=stk.name))
        lNameCb.append(stk.name)
    pl.title('[bar-chart] sleep on sections')
    ax.legend(lNameCb)
    pl.xlabel('time (unit: day)')
    pl.ylabel('sleep level (unit: seconds)')
    pl.ylim(0, 43200)


def drawFoodDistCurveWith(lNpFStock, fig, rSelected=None, lColors='bgrcmk'):  # draw sleep (per time units) curves for FlyStock list [lFStock]
    assert isinstance(lNpFStock, list)
    pl.style.use('bmh')
    lPlots = []
    lNameCb = []
    ax = fig.add_subplot(111)
    interv = 1800.0
    timestep = 3600.0 / interv
    for i, stk in enumerate(lNpFStock):
        assert isinstance(stk, NumpyFlyStock)
        matDataSect, vAvgDataSect, vSemDataSect = stk.getSectData(interv=interv)
        if not rSelected:
            vTime = np.arange(1, int(stk.nUnitTime / interv) + 1, dtype=float) / timestep
            vData = vAvgDataSect
            vSem = vSemDataSect
        else:
            vTime = np.arange(int(rSelected[0] * timestep), int(rSelected[-1] * timestep), timestep)
            vData = vAvgDataSect[int(rSelected[0] * timestep):int(rSelected[-1] * timestep)]
            vSem = vSemDataSect[int(rSelected[0] * timestep):int(rSelected[-1] * timestep)]
        print 'vTime size = %d; vData size = %d' % (vTime.size, vData.size)
        ax.plot(vTime, vData, picker=True, label=stk.name)
        thisPlot = ax.errorbar(vTime, vData, yerr=vSem, label=stk.name)
        pl.setp(thisPlot, color=lColors[i])
        lPlots.append(thisPlot)
        lNameCb.append(stk.name)
    pl.title('food distance curve on 30-min')
    pl.legend(lPlots, lNameCb, loc='best')
    pl.xlabel('time (unit: hour)')
    pl.ylabel('distance (unit: %)')
    # pl.ylim(0,100)


def drawFoodDistHistogramWith(lNpFStock, rSelected=None, outDir=None):
    assert isinstance(lNpFStock, list)
    fig = pl.figure()
    for i, stk in enumerate(lNpFStock):
        lTime = []
        lDist = []
        assert isinstance(stk, NumpyFlyStock)
        nUnitPerSect = 1800
        if rSelected:
            matDataRaw = stk.matDataRaw[:, rSelected[0] * nUnitPerSect : rSelected[-1] * nUnitPerSect]
        else:
            matDataRaw = stk.matDataRaw
        lTime = np.zeros(matDataRaw.shape)
        for t in range(stk.nUnitTime / nUnitPerSect):
            lTime[:, t * nUnitPerSect : (t+1) * nUnitPerSect] = float(t * nUnitPerSect) / 3600.0
        lTime = lTime.transpose().reshape((lTime.size,))
        lDist = matDataRaw.transpose().reshape((matDataRaw.size,))

        pl.title(stk.name)
        if rSelected:
            pl.hist2d(lTime, lDist, bins=[int(rSelected[-1] - rSelected[0]), 100])
        else:
            pl.hist2d(lTime, lDist, bins=[int(stk.nUnitTime / nUnitPerSect), 100])
        pl.colorbar()
        if outDir:
            fig.savefig(os.path.join(outDir, (stk.name + '-heatmap.png')))
            fig.savefig(os.path.join(outDir, (stk.name + '-heatmap.svg')))


def drawFoodDistRatioWith(lFStock, fig, rSelected=None, lColors='bgrcmk'):
    assert isinstance(lFStock, list)
    llRet = []
    lPlots = []
    ax = fig.add_subplot(111)
    for i, stk in enumerate(lFStock):
        lTime = []
        lFreqDistNear = []
        lFreqDistFar = []
        lRatioDistN2F = []
        for t in range(stk.nUnitTime):
            lFreqDistNear.append(0.0)
            lFreqDistFar.append(0.0)
            lRatioDistN2F.append(0.0)
        assert isinstance(stk, FlyStock)
        for lD in stk.matDataRaw:
            for t, d in enumerate(lD):
                if rSelected and t < int(rSelected[0] * 2 - 1):
                    lFreqDistNear[t] = 1.0
                if rSelected and t >= int(rSelected[-1] * 2 - 1):
                    lFreqDistNear[t] = 1.0
                if d < 40:
                    lFreqDistNear[t] += 1.0
                else:
                    lFreqDistFar[t] += 1.0
        for t in range(stk.nUnitTime):
            lRatioDistN2F[t] = lFreqDistNear[t] / (lFreqDistNear[t] + lFreqDistFar[t])
        if not rSelected:
            oneplot, = ax.plot(stk.lTime, lRatioDistN2F, picker=True, label=stk.name, c=lColors[i])
            lPlots.append(oneplot)
        else:
            oneplot, = ax.plot(stk.lTime[int(rSelected[0] * 2):int(rSelected[-1] * 2)],
                    lRatioDistN2F[int(rSelected[0] * 2):int(rSelected[-1] * 2)], picker=True, label=stk.name)
            lPlots.append(oneplot)
        pl.legend(handles=lPlots)
        llRet.append(lRatioDistN2F)
    return llRet


def testDrawCurveSleepRaw():
    fBefore = 'D:/video/20151029-1105_M1KO-sd_stv/duringStv/sleep_30mins_CT.txt'
    dBeforeStocks = createFlyStocksWith(fBefore)
    for stk in dBeforeStocks.values():
        print stk
    drawSleepRawCurveWith(dBeforeStocks.values())
    pl.show()


def testDrawSleepSectCurveWith():
    fBefore = 'D:/video/20151029-1105_M1KO-sd_stv/duringStv/sleep_30mins_CT.txt'
    dBeforeStocks = createFlyStocksWith(fBefore)
    for stk in dBeforeStocks.values():
        print stk
    drawSleepSectCurveWith(dBeforeStocks.values())
    pl.show()


def testDrawFoodDistCurveWith():
    fBefore = 'D:/video/20151023-1028_M1KO-sd/beforeSD/foodDistance_croosBeam_v2.mat'
    dBeforeStocks = createFlyStocksFromMat(fBefore)
    for stk in dBeforeStocks.values():
        print stk
    fig = pl.figure()
    drawFoodDistCurveWith(dBeforeStocks.values(), fig)
    pl.show()


def testDrawFoodDistHistogramWith():
    fBefore = 'D:/video/20151023-1028_M1KO-sd/beforeSD/foodDistance_croosBeam_v2.mat'
    fOut = 'D:/video/20151023-1028_M1KO-sd/beforeSD/summary'
    dBeforeStocks = createFlyStocksFromMat(fBefore)
    for stk in dBeforeStocks.values():
        print stk
    drawFoodDistHistogramWith(dBeforeStocks.values(), None, fOut)
    # pl.show()


def testDrawFoodDistRatioWith():
    fBefore = 'D:/video/20151023-1028_M1KO-sd/beforeSD/food_distance_30CT.txt'
    dBeforeStocks = createFlyStocksWith(fBefore)
    print dBeforeStocks.values()[0].nUnitTime
    llRatio = drawFoodDistRatioWith(dBeforeStocks.values(), range(24,120))
    pl.show()
    fid = open('D:/video/20151023-1028_M1KO-sd/beforeSD/friendly_summary/nearfoodratio.txt', 'w')
    for i, lRatio in enumerate(llRatio):
        fid.write('stock %s\n'% dBeforeStocks.values()[i].name)
        for t in range(dBeforeStocks.values()[i].nUnitTime):
            fid.write('%.1f\t' % (float(t) * 0.5))
        fid.write('\n')
        for v in lRatio:
            fid.write('%f\t' % v)
        fid.write('\n')
    fid.close()


# testDrawCurveSleepRaw()
# testDrawSleepSectCurveWith()
# testDrawFoodDistCurveWith()
# testDrawFoodDistHistogramWith()
# testDrawFoodDistRatioWith()