import math
import numpy as np


class FlyStock(object):
    def __init__(self, name=None, nUnitTime=0):
        self.name = name  # the stock name
        self.nUnitTime = nUnitTime  # the time length counted on units, e.g. 1 sec or 1 half-hour
        self.nLiveFly = 0  # the number of flies alive, i.e. the row number
        self.matDataRaw = []  # matrix of raw data per Raw-min
        self.lIdxFly = []  # the list of original indices for each fly
        self.lTime = []  # time axis on half-hour, e.g. [0, 0.5, 1, 1.5, etc.]
        self.lNotBlank = []  # the number of valid data points for each column
        self.lSumDataRaw = []  # list of sum data over all flies in current stock (fcs)
        self.lAvgDataRaw = []  # list of average data over fcs
        self.lSumSqrDataRaw = []  # list of sum square error over fcs
        self.lSemDataRaw = []  # list of S.E.M. over fcs
        for i in range(nUnitTime):
            self.lTime.append(i * 0.5)
            self.lNotBlank.append(0)
            self.lSumDataRaw.append(0.0)
            self.lAvgDataRaw.append(0.0)
            self.lSumSqrDataRaw.append(0.0)
            self.lSemDataRaw.append(0.0)

    def __str__(self):
        return "[FlyStock] name: %s, fly number: %d, putative hours: %d" \
               % (self.name, self.nLiveFly, self.nUnitTime / 2 - 24)

    def _elementWise(self, lA, lB, func):
        assert len(lA) == len(lB)
        lC = []
        for i, a in enumerate(lA):
            lC.append(func(a, lB[i]))
        return lC

    def _addEw(self, lA, lB):
        assert len(lA) == len(lB)
        lC = []
        for i, a in enumerate(lA):
            lC.append(a + lB[i])
        return lC

    def _divideEw(self, lA, b):
        lC = []
        for i, a in enumerate(lA):
            lC.append(a / b)
        return lC

    def push(self, lDataRaw, idxFly):  # append a new fly data, with unique index in the stock
        self.nLiveFly += 1
        self.lIdxFly.append(idxFly)
        self.matDataRaw.append([])
        assert isinstance(self.matDataRaw[-1], list)
        for i, DataRaw in enumerate(lDataRaw):  # update sum
            self.matDataRaw[-1].append(DataRaw)
            self.lSumDataRaw[i] += DataRaw
            self.lAvgDataRaw[i] = self.lSumDataRaw[i] / self.nLiveFly
            self.lSumSqrDataRaw[i] += (DataRaw - self.lAvgDataRaw[i]) ** 2
            self.lSemDataRaw[i] = math.sqrt(self.lSumSqrDataRaw[i]) / self.nLiveFly

    def join(self, other):  # stitch the other same stock at tail
        assert isinstance(other, FlyStock)
        if self.name != other.name or self.nUnitTime != other.nUnitTime:
            return
        for i in range(other.nLiveFly):
            other.lIdxFly[i] += self.lIdxFly[-1]
        self.lIdxFly += other.lIdxFly
        self.matDataRaw += other.matDataRaw
        self.lSumDataRaw = self._addEw(self.lSumDataRaw, other.lSumDataRaw)
        self.nLiveFly += other.nLiveFly
        self.lAvgDataRaw = self._divideEw(self.lSumDataRaw, self.nLiveFly)
        for i, lDataRaw in enumerate(self.matDataRaw):  # for each fly
            for t, DataRaw in enumerate(lDataRaw):  # for each unit time
                self.lSumSqrDataRaw[t] += (DataRaw - self.lAvgDataRaw[i]) ** 2  # update variance
        self.lSemDataRaw[i] = self._divideEw(self.lSumSqrDataRaw[i], self.nLiveFly)

    def getSectionData(self):
        nSection = int(self.nUnitTime / 24)  # number of sections, 12 hour per section
        matDataSect = []  # Matrix of section data, [nFly x nSection]
        lSumDataSect = []  # list of sum section data, [nSection]
        lAvgDataSect = []  # list of mean section data, [nSection]
        lSumSqrDataSect = []  # list of sum-square-error section data, [nSection]
        lSemDataSect = []  # list of S.E.M. section data, [nSection]
        for i in range(self.nLiveFly):  # initialise section related data
            matDataSect.append([])
        for i in range(nSection):
            lSumDataSect.append(0.0)
            lAvgDataSect.append(0.0)
            lSumSqrDataSect.append(0.0)
            lSemDataSect.append(0.0)
        ## compute section data matrix
        for iFly, fly in enumerate(self.matDataRaw):  # for each fly
            for iSect in range(nSection):  # for each section
                matDataSect[iFly].append(sum(fly[iSect*24:(iSect+1)*24]))  # sum up current section data
                lSumDataSect[iSect] += matDataSect[iFly][-1]  # sum up current section data for all flies
        ## compute mean data per section
        for iSect in range(nSection):
            lAvgDataSect[iSect] = lSumDataSect[iSect] / self.nLiveFly
        ## compute sum of square-error per section
        for iFly, fly in enumerate(matDataSect):
            for iSect in range(nSection):
                lSumSqrDataSect[iSect] += (fly[iSect] - lAvgDataSect[iSect]) ** 2
        ## compute S.E.M. data per section
        for iSect in range(nSection):
            lSemDataSect[iSect] = math.sqrt(lSumSqrDataSect[iSect]) / self.nLiveFly
        ## return lSection, lAvgDataSect, lSemDataSect
        return nSection, lAvgDataSect, lSemDataSect, matDataSect

    def getIdxRowWith(self, idxFly):  # convert from fly-index to row-index in data matrix, ret=-1 means not in record
        for iR, iF in enumerate(self.lIdxFly):
            if idxFly == iF:
                return iR
        return -1


class NumpyFlyStock(object):
    def __init__(self, name, nUnitTime):
        self.name = name  # the stock name
        self.nUnitTime = nUnitTime  # the time length counted on units, e.g. 1 sec or 1 half-hour
        self.nLiveFly = 0  # the number of flies alive, i.e. the row number
        self.matDataRaw = np.ndarray([])  # matrix of raw data per Raw-min
        self.vIdxFly = np.ndarray([])  # the vector of original indices for each fly
        self.vTime = np.arange(nUnitTime, dtype=np.float) # time axis unitTime
        self.vAvgDataRaw = np.zeros(nUnitTime, dtype=np.float)  # vector of average data over fcs
        self.vSemDataRaw = np.zeros(nUnitTime, dtype=np.float)  # vector of S.E.M. over fcs

    def __str__(self):
        return "[FlyStock] name: %s, fly number: %d, putative hours: %.2f, putative seconds: %d" \
               % (self.name, self.nLiveFly, self.nUnitTime / 3600.0, self.nUnitTime)

    def push(self, matData):
        assert isinstance(matData, np.ndarray)
        assert isinstance(self.matDataRaw, np.ndarray)
        self.nLiveFly += matData.shape[0]
        if self.matDataRaw.ndim == 0:
            self.matDataRaw = matData
        else:
            timeDiff = self.matDataRaw.shape[1] - matData.shape[1]
            if timeDiff == 0:  # time axes are consistent
                self.matDataRaw = np.append(self.matDataRaw, matData, axis=0)
            elif timeDiff > 0:  # original time axis is longer
                self.nUnitTime -= timeDiff
                self.matDataRaw = np.append(self.matDataRaw[:, 0 : self.nUnitTime], matData, axis=0)
            else:  # input data mat is longer
                self.matDataRaw = np.append(self.matDataRaw, matData[:, 0 : self.nUnitTime], axis=0)
        self.vAvgDataRaw = self.matDataRaw.mean(axis=0)
        self.vSemDataRaw = self.matDataRaw.std(axis=0) / math.sqrt(self.nLiveFly)

    def getSectData(self, interv=1800):
        matDataSect = np.ndarray((self.matDataRaw.shape[0], self.nUnitTime / interv),
                                 dtype=self.matDataRaw.dtype)
        for iS in range(int(self.nUnitTime / interv)):
            matDataSect[:, iS] = self.matDataRaw[:, iS * interv : (iS + 1) * interv].mean(axis=1)
        vAvgDataSect = matDataSect.mean(axis=0)
        vSemDataSect = matDataSect.std(axis=0) / math.sqrt(self.nLiveFly)
        return matDataSect, vAvgDataSect, vSemDataSect
