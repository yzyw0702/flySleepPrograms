import string
from MFlyStock import *
from MMatParser import *
import matplotlib.pyplot as pl


def indexWith(srcList, name):
    for i, s in enumerate(srcList, name):
        if s == name:
            return i
    return -1


def createFlyStocksWith(inputFile):
    try:
        fid = open(inputFile, 'r')  # open mean_sleep_30mins_CT.txt
    except IOError:
        return None
    ## extract dimensional properties
    lData30 = fid.readlines()  # read a list of 30min-sleep over time
    nTimeUnit = len(lData30[0].split('\t')) - 2  # count how many 30 min in total
    ## create time line, unit: hr
    lTime = []
    for i in range(nTimeUnit):  # 0.5, 1.0, 1.5, etc.
        lTime.append(i * 0.5)
    ## create list of stock names
    dStocks = {}  # dictionary of fly stock objects: name_string -> FlyStock
    for i, fly in enumerate(lData30):  # get a non-redundant list of stock name
        flydata = fly.split('\t')  # parse raw data list
        currName = flydata[0].rstrip(':')  # get current fly's stock name
        if currName not in dStocks:  # current name is not recorded yet
            dStocks[currName] = FlyStock(currName, nTimeUnit)
        flyData = []
        isValid = False
        for s in flydata[1:-1]:
            if len(s) == 0:
                flyData.append(-0.0001)
            else:
                isValid = True
                flyData.append(string.atof(s))
        assert isinstance(dStocks[currName], FlyStock)
        if isValid:
            dStocks[currName].push(flyData, i)
    fid.close()
    return dStocks


def createFlyStocksFromMat(inputFile):
    lStockName, cubeDist = loadDistMat(inputFile)
    dStocks = {}
    for i, name in enumerate(lStockName):
        name = name.rstrip(':')
        matDist = np.array(cubeDist[i])
        lIdxDead = []
        for iFly in range(matDist.shape[0]):
            if matDist[iFly, 0] == -1:
                lIdxDead.append(iFly)  # label dead fly data
        matDist = np.delete(matDist, lIdxDead, axis=0)  # delete dead fly data
        if name in dStocks.keys():
            dStocks[name].push(matDist)
        else:
            stk = NumpyFlyStock(name, matDist.shape[1])
            stk.push(matDist)
            dStocks[name] = stk
    return dStocks


def test_createFlyStocksWith():
    pathFile = 'D:/video/20151029-1105_M1KO-sd_stv/beforeStv/sleep_30mins_CT.txt'
    dStocks = createFlyStocksWith(pathFile)
    aStock = dStocks.values()[0]
    assert isinstance(aStock, FlyStock)
    print "half hour number: %d" % aStock.nUnitTime
    print "stock number: %d" % len(dStocks)
    for i, stk in enumerate(dStocks.values()):
        assert isinstance(stk, FlyStock)
        print "stock-#%d, <%s>, contains %d flies." % (i, stk.name, stk.nLiveFly)


def test_createFlyStocksFromMat():
    pathFile = 'D:/video/20151023-1028_M1KO-sd/beforeSD/foodDistance_croosBeam_v2.mat'
    dStocks = createFlyStocksFromMat(pathFile)
    fig = pl.figure()
    ax = fig.add_subplot(111)
    lPlots = []
    lNames = []
    for i, stk in enumerate(dStocks.values()):
        print stk
        assert isinstance(stk, NumpyFlyStock)
        matSect, vAvgSect, vSemSect = stk.getSectData(1800)
        ax.plot(np.arange(stk.nUnitTime / 1800), vAvgSect, label=stk.name)
        lPlots.append(ax.errorbar(np.arange(stk.nUnitTime / 1800), vAvgSect, yerr=vSemSect))
        lNames.append(stk.name)
    ax.legend(lPlots,lNames)
    pl.show()


# test_createFlyStocksWith()
# test_createFlyStocksFromMat()