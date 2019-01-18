import os
import shutil


def classifyFiles(rootPath):
    lFiles = os.listdir(rootPath)
    lAvi = []
    llAvi = []
    lDir = []
    for f in lFiles:  # filter all avi video clips
        if ".avi" in f:
            dirName = f.rstrip()[0:3]
            if dirName not in lDir:
                if len(lAvi) > 0:
                    llAvi.append(lAvi)
                lAvi = []
                lDir.append(dirName)
            lAvi.append(f.rstrip())
    llAvi.append(lAvi)
    return llAvi, lDir


def packageFiles(rootPath, llFiles, lDir):
    for i, Dir in enumerate(lDir):
        lFiles = llFiles[i]
        print '%%%% package ch-%s files %%%%' % Dir
        pathDir = os.path.join(rootPath, Dir)
        if not os.path.exists(pathDir):
            os.mkdir(pathDir)
        for f in lFiles:
            srcF = os.path.join(rootPath, f)
            dstF = os.path.join(rootPath, Dir, f)
            shutil.move(srcF, dstF)


def filterAndMove(rootPath):
    llAvi, lDir = classifyFiles(rootPath)
    packageFiles(rootPath, llAvi, lDir)


def listFiles(rootPath):
    lDir = []
    for Dir in os.listdir(rootPath):
        if '00' in Dir and len(Dir) <= 3:
            lDir.append(Dir)
    lAvi = []
    for Dir in lDir:
        pathDir = os.path.join(rootPath, Dir)
        lAvi = []
        for f in os.listdir(pathDir):
            if '.avi' in f:
                lAvi.append(f)
        pathLog = os.path.join(pathDir, 'list.txt')
        if not os.path.exists(pathLog):
            fLog = open(pathLog, 'w')
            for f in lAvi:
                fLog.write(f+'\n')
            fLog.close()


rootPath = "./"
filterAndMove(rootPath)
listFiles(rootPath)