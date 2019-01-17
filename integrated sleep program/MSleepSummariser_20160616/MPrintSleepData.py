from MCreateFlyStock import *
import os


def writeSleepSectionWith(fStock, hOutput):
    assert isinstance(fStock, FlyStock)
    nSection, lAvgSlpData, lSemSlpData, matSlpSect = fStock.getSectionData()
    hOutput.write("index\t")
    for i in range(nSection): # write title
        iDay = int(i / 2)
        if i % 2 == 0:
            hOutput.write('%s-day%d' % (fStock.name, iDay + 1))
        else:
            hOutput.write('%s-night%d' % (fStock.name, iDay + 1))
        if i < nSection - 1:
            hOutput.write('\t')
        else:
            hOutput.write('\n')
    for iF in range(fStock.nLiveFly):  # output data matrix
        hOutput.write("%s\t" % fStock.lIdxFly[iF])
        for iS in range(nSection):
            hOutput.write('%.1f' % matSlpSect[iF][iS])
            if iS < nSection - 1:
                hOutput.write('\t')
            else:
                hOutput.write('\n')


def batchWriteSleepSection(fStocks, outDir):
    for i, fs in enumerate(fStocks):
        fOut = os.path.join(outDir, 'sleep_per_section - stock-%d_%s.txt' % (i + 1, fs.name))
        fid = open(fOut, 'w')
        assert isinstance(fs, FlyStock)
        writeSleepSectionWith(fs, fid)
        fid.close()


def writeSleepSectionMeanWith(fStock, hOutput):
    assert isinstance(fStock, FlyStock)
    hOutput.write('stock_name\t%s\t' % fStock.name)
    hOutput.write('sample_size\t%d\n' % fStock.nLiveFly)
    nSection, lAvgSlpData, lSemSlpData, matSlpSect = fStock.getSectionData()
    for i in range(nSection): # write title
        iDay = int(i / 2)
        if i % 2 == 0:
            hOutput.write('day-%d' % (iDay + 1))
        else:
            hOutput.write('night-%d' % (iDay + 1))
        if i < nSection - 1:
            hOutput.write('\t')
        else:
            hOutput.write('\n')
    for iS in range(nSection):
        hOutput.write('%.1f\t' % lAvgSlpData[iS])
    hOutput.write('\n')
    for iS in range(nSection):
        hOutput.write('%.1f\t' % lSemSlpData[iS])
    hOutput.write('\n')


def batchWriteSleepSectionMean(fStocks, outDir):
    fOut = os.path.join(outDir, 'mean-sem_sleep_per_section.txt')
    fid = open(fOut, 'w')
    for i, fs in enumerate(fStocks):
        assert isinstance(fs, FlyStock)
        writeSleepSectionMeanWith(fs, fid)
    fid.close()


def writeSleepRawMeanWith(fStock, hOutput):
    assert isinstance(fStock, FlyStock)
    hOutput.write('stock_name\t%s\t' % fStock.name)
    hOutput.write('sample_size\t%d\n' % fStock.nLiveFly)
    for t in fStock.lTime:  # write time line
        hOutput.write('%.1f\t' % (t + 0.5))
    hOutput.write('\n')
    for v in fStock.lAvgDataRaw:
        hOutput.write('%f\t' % v)
    hOutput.write('\n')
    for v in fStock.lSemDataRaw:
        hOutput.write('%f\t' % v)
    hOutput.write('\n')


def batchWriteSleepRawMean(fStocks, outDir):
    fInput = os.path.join(outDir, 'mean-sem_sleep30min.txt')
    fid = open(fInput, 'w')
    for stk in fStocks:
        writeSleepRawMeanWith(stk, fid)
    fid.close()


def writeFoodDistCurveMeanWith(fStock, hOutput):  # draw sleep (per time units) curves for FlyStock list [lFStock]
    assert isinstance(fStock, FlyStock)
    assert isinstance(fStock, FlyStock)
    hOutput.write('stock_name\t%s\t' % fStock.name)
    hOutput.write('sample_size\t%d\n' % fStock.nLiveFly)
    for t in fStock.lTime:  # write time line
        hOutput.write('%.1f\t' % (t + 0.5))
    hOutput.write('\n')
    for v in fStock.lAvgDataRaw:
        hOutput.write('%f\t' % v)
    hOutput.write('\n')
    for v in fStock.lSemDataRaw:
        hOutput.write('%f\t' % v)
    hOutput.write('\n')


def writeFoodDistRatio(fStocks, llRatio, outDir):
    fid = open(os.path.join(outDir, 'nearfoodratio.txt'), 'w')
    for i, lRatio in enumerate(llRatio):
        fid.write('stock %s\n'% fStocks[i].name)
        for t in range(fStocks[i].nUnitTime):
            fid.write('%.1f\t' % (float(t) * 0.5))
        fid.write('\n')
        for v in lRatio:
            fid.write('%f\t' % v)
        fid.write('\n')
    fid.close()


def batchWriteFoodDistCurveMean(fStocks, outDir):
    fInput = os.path.join(outDir, 'mean-sem_foodDist30min.txt')
    fid = open(fInput, 'w')
    for stk in fStocks:
        writeFoodDistCurveMeanWith(stk, fid)
    fid.close()


def testwriteSleepSectionWith():
    inFile = 'D:/video/20151023-1028_M1KO-sd/beforeSD/sleep_30mins_CT.txt'
    outDir = 'D:/video/20151023-1028_M1KO-sd/beforeSD/friendly_summary'
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    dStocks = createFlyStocksWith(inFile)
    batchWriteSleepSection(dStocks.values(), outDir)


def testwriteSleepSectionMean():
    inFile = 'D:/video/20151029-1105_M1KO-sd_stv/duringStv/sleep_30mins_CT.txt'
    outDir = 'D:/video/20151029-1105_M1KO-sd_stv/duringStv/friendly_summary'
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    dStocks = createFlyStocksWith(inFile)
    batchWriteSleepSectionMean(dStocks.values(), outDir)


def testwriteSleepRawWithMean():
    inFile = 'D:/video/20151029-1105_M1KO-sd_stv/duringStv/sleep_30mins_CT.txt'
    outDir = 'D:/video/20151029-1105_M1KO-sd_stv/duringStv/friendly_summary'
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    dStocks = createFlyStocksWith(inFile)
    batchWriteSleepRawMean(dStocks.values(), outDir)


def testBatchWriteFoodDistCurveMean():
    inFile = 'D:/video/20151029-1105_M1KO-sd_stv/duringStv/food_distance_30CT.txt'
    outDir = 'D:/video/20151029-1105_M1KO-sd_stv/duringStv/friendly_summary'
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    dStocks = createFlyStocksWith(inFile)
    batchWriteFoodDistCurveMean(dStocks.values(), outDir)


# testwriteSleepSectionWith()
# testwriteSleepRawWithMean()
# testwriteSleepSectionMean()
# testBatchWriteFoodDistCurveMean()