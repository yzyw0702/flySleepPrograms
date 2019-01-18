__author__ = 'youngway'
import os


def getAllSubDir(dRoot):
    lAllDir = []  # store all directories
    lSub = os.listdir(dRoot)
    for p in lSub:
        absPath = os.path.join(dRoot, p)
        if os.path.isdir(absPath):
            lAllDir.append(absPath)
            lAllDir = lAllDir + getAllSubDir(absPath)
    return lAllDir


def main():
    ## get all subdirectories within range
    fRange = raw_input('set input range list: ')  # get search range
    hRange = open(fRange, 'r')
    lDirs = []  # get all target directories by traversing within search range
    for task in hRange.readlines():
        lDirs = lDirs + getAllSubDir(task.rstrip())
    hRange.close()
    # filter the real target directories
    lTargets = []  # save all directories that contain data
    for subdir in lDirs:
        lFiles = os.listdir(subdir)
        if ('bg.png' in lFiles) or ('background.png' in lFiles) \
                and ('config.yaml' in lFiles):
            lTargets.append(subdir)
    ## save these targets
    hRange = open('1-1_listsrc.txt', 'w')  # save into this file
    for r in lTargets:
        hRange.write('%s\n' % r)
    hRange.close()


def test():
    testRoot = 'E:/kanbox/computer science/training_projects/'
    print getAllSubDir(testRoot)

main()