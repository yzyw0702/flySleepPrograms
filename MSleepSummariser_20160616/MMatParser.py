import h5py


def ascii2str(llAscii):
    return ''.join(chr(w[0]) for w in llAscii)


def loadDistMat(pathInput):
    """
    load food-distance matrix from .mat file (MATLAB .mat v7.3)
    :param pathInput: absolute path to foodDistance_croosBeam_v2.mat
    :returns (lStockName, cubeDist): List of stock name, numpy data cube of food distance (nStock x nFly x nSeconds)
    """
    h5fid = h5py.File(pathInput, 'r')
    for item in h5fid.keys():
        print item + ':', h5fid[item]
    # data matrices
    rl = h5fid['ranged_location']
    lStockName = []  # nStock
    cubeDist = []  # nStock x nFly x nSeconds
    for i, lIdx in enumerate(rl):  # for each column
        if i==0:  # get stock name
            for idx in lIdx:
                lStockName.append(ascii2str(h5fid[idx]))
        elif i==3:  # get food-distance matrix
            for idx in lIdx:
                cubeDist.append(h5fid[idx].value)
    # print llMatDist[0][0][0:12]
    h5fid.close()
    return lStockName, cubeDist


def testLoadDistMat():
    pathIn = 'D:/video/20151023-1028_M1KO-sd/beforeSD/foodDistance_croosBeam_v2.mat'
    lStockName, cubeDist = loadDistMat(pathIn)
    for i, name in enumerate(lStockName):
        print 'stock <%s> contains %d flies, each fly contains %d seconds data.' % (name, len(cubeDist[i]), len(cubeDist[i][0]))

# testLoadDistMat()