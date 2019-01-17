# coding=utf-8
import Tkinter as tk
import os
import string as ss
import tkFileDialog as win
from matplotlib.image import AxesImage
from MDrawSleepCharts import *
from MPrintSleepData import *

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        # data storage
        self.dStockSleepRaw = None
        self.dStockDistRaw = None
        self.pathRoot = 'rootpath'
        self.rSelected = None
        self.llFoodDistRatio = []
        self.lColors = []

        # frame for buttons
        self.frBtn = tk.LabelFrame(self, text=u'功能')
        self.frBtn.pack(side=tk.TOP)
        # frame for statii
        self.frStatusPath = tk.LabelFrame(self, text=u'目标文件')
        self.frStatusPath.pack(side=tk.TOP)
        self.frStatusOp = tk.LabelFrame(self, text=u'当前操作状态')
        self.frStatusOp.pack(side=tk.TOP)
        # frame for range-input box
        self.frRange = tk.LabelFrame(self, text=u'选择范围')
        self.frRange.pack(side=tk.TOP)

        # widget show-usage button
        self.btShowUsage = tk.Button(self.frBtn)
        self.btShowUsage['text'] = u'使用方法'
        self.btShowUsage['command'] = self.onShowUsage
        self.btShowUsage.pack(side=tk.LEFT)
        # widget set-path button
        self.btSetPath = tk.Button(self.frBtn)
        self.btSetPath['text'] = u'打开路径'
        self.btSetPath['command'] = self.onSetPath
        self.btSetPath.pack(side=tk.LEFT)
        # widget preview button
        self.btPreview = tk.Button(self.frBtn)
        self.btPreview['text'] = u'预览'
        self.btPreview['command'] = self.onPreview
        self.btPreview['state'] = tk.DISABLED
        self.btPreview.pack({'side': 'left'})
        # widget output figures
        self.btSaveFig = tk.Button(self.frBtn, text=u'导出图片')
        self.btSaveFig['command'] = self.onSaveFig
        self.btSaveFig['state'] = tk.DISABLED
        self.btSaveFig.pack(side='left')
        # widget print data sheets
        self.btPrintData = tk.Button(self.frBtn)
        self.btPrintData['text'] = u'导出数据表'
        self.btPrintData['command'] = self.onPrintData
        self.btPrintData['state'] = tk.DISABLED
        self.btPrintData.pack(side=tk.LEFT)
        # widget close all figures
        self.btCloseAll = tk.Button(self.frBtn)
        self.btCloseAll['text'] = u'关闭所有图片'
        self.btCloseAll['command'] = self.onCloseAll
        self.btCloseAll.pack(side=tk.LEFT)
        # widget quit button
        self.btQuit = tk.Button(self.frBtn)
        self.btQuit['text'] = u'退出'
        self.btQuit['command'] = self.quit
        self.btQuit.pack(side=tk.LEFT)
        # widget edit / preview path text
        self.lbPath = tk.Label(self.frStatusPath, font='TimesNewRoman')
        self.lbPath['text'] = u'选择或在以下文本框中输入目标文件夹'
        self.lbPath.pack(side=tk.TOP)
        self.entPath = tk.Entry(self.frStatusPath, font='TimesNewRoman')
        self.entPath.bind('<Key-Return>', self.onEntrySetPath)
        self.entPath.pack(side=tk.TOP)
        # widget operation statii text
        self.lbStatusOp = tk.Label(self.frStatusOp, font='TimesNewRoman', justify='left')
        self.lbStatusOp['text'] = 'select range after preview'
        self.lbStatusOp.pack(side=tk.TOP)
        # widget entry ask to select range
        self.lbFrom = tk.Label(self.frRange, text='from', font='TimesNewRoman')
        self.lbFrom.pack(side=tk.LEFT)
        self.entFrom = tk.Entry(self.frRange)
        self.entFrom['text'] = 0
        self.entFrom['state'] = tk.DISABLED
        self.entFrom.pack(side=tk.LEFT)
        self.lbTo = tk.Label(self.frRange, text='to', font='TimesNewRoman')
        self.lbTo.pack(side=tk.LEFT)
        self.entTo = tk.Entry(self.frRange)
        self.entTo['text'] = 0
        self.entTo['state'] = tk.DISABLED
        self.entTo.pack(side=tk.LEFT)
        self.btSetRange = tk.Button(self.frRange, text=u'确认')
        self.btSetRange['command'] = self.onSetRange
        self.btSetRange.pack(side=tk.LEFT)

    def disableFunc(self, message=''):
        self.lbPath['text'] = 'invalid path'
        self.lbStatusOp['text'] = message
        self.lbPath['fg'] = 'red'
        self.btPreview['state'] = tk.DISABLED
        self.btPrintData['state'] = tk.DISABLED
        self.entFrom['state'] = tk.DISABLED
        self.entTo['state'] = tk.DISABLED

    def onSetPath(self):
        self.pathRoot = win.askdirectory(initialdir='C:/')
        if os.path.exists(self.pathRoot):
            self.lbPath['text'] = self.pathRoot
            self.lbPath['fg'] = 'black'
            self.btPreview['state'] = tk.NORMAL
            self.dStockSleepRaw = createFlyStocksWith(os.path.join(self.pathRoot, 'sleep_30mins_CT.txt'))
            if not self.dStockSleepRaw:
                self.disableFunc('no sleep_30min_CT.txt in such path')
                return
            self.dStockDistRaw = createFlyStocksWith(os.path.join(self.pathRoot, 'food_distance_30CT.txt'))
            if not self.dStockSleepRaw:
                self.disableFunc('no food_distance_30CT.txt in such path')
                return
            self.lColors = np.random.rand(len(self.dStockSleepRaw), 3)
        else:
            self.disableFunc()

    def onEntrySetPath(self, event):
        self.pathRoot = self.entPath.get()
        if os.path.exists(self.pathRoot):
            self.lbPath['text'] = self.pathRoot
            self.lbPath['fg'] = 'black'
            self.btPreview['state'] = tk.NORMAL
            self.dStockSleepRaw = createFlyStocksWith(os.path.join(self.pathRoot, 'sleep_30mins_CT.txt'))
            if not self.dStockSleepRaw:
                self.disableFunc('no sleep_30min_CT.txt in such path')
                return
            self.dStockDistRaw = createFlyStocksWith(os.path.join(self.pathRoot, 'food_distance_30CT.txt'))
            if not self.dStockSleepRaw:
                self.disableFunc('no food_distance_30CT.txt in such path')
                return
            self.lColors = np.random.rand(len(self.dStockSleepRaw), 3)
        else:
            self.disableFunc()

    def onShowUsage(self):
        sUsage = \
                u'1. 选择或输入目标文件夹（包含 sleep_30min_CT.txt 和 food_distance_30CT.txt）；\n' \
                u'2. 点击 [预览]；\n' \
                u'3. 在 <选择范围> 一栏中，设置从多少小时到多少小时（精确到0.5），点击[确认]就会截取目标数据；\n' \
                u'4. 查看弹出的数据图（很多），如果感觉截取范围不满意，可以修改后再次点击确认；\n' \
                u'5. 点击 [导出数据表]，会导出没有截取范围的数据，导出目录见 <status> 一栏；\n' \
                u'6. 多次点击[退出]即可正常关闭程序\n'
        self.lbPath['text'] = u'选择或在以下文本框中输入目标文件夹'
        self.lbStatusOp['text'] = sUsage

    def onPreview(self):
        print '====== [preview] ======'
        for stk in self.dStockSleepRaw.values():
            print stk
        self.entFrom['state'] = tk.NORMAL
        self.entTo['state'] = tk.NORMAL
        self.btPrintData['state'] = tk.NORMAL
        self.btSaveFig['state'] = tk.NORMAL
        if not self.rSelected:
            astk = self.dStockSleepRaw.values()[0]
            assert isinstance(astk, FlyStock)
            self.entFrom['text'] = 0
            self.entTo['text'] = astk.nUnitTime
        fig11 = pl.figure()
        drawSleepRawCurveWith(self.dStockSleepRaw.values(), fig11, self.rSelected, self.lColors)
        fig11.canvas.mpl_connect('pick_event', self.onPick)
        pl.show()

    def onSetRange(self):
        vFrom = self.entFrom.get()
        vTo = self.entTo.get()
        if len(vFrom) == 0 or len(vTo)==0:
            return
        if self.isNum(vFrom) and self.isNum(vTo):
            self.rSelected = [ss.atof(vFrom), ss.atof(vTo)]
            sStatus = 'selected from %.1f to %.1f.' % (self.rSelected[0], self.rSelected[-1])
            self.lbStatusOp['text'] = sStatus
            self.lbStatusOp['fg'] = 'black'
        else:
            self.lbStatusOp['text'] = 'invalid range'
            self.lbStatusOp['fg'] = 'red'
            self.rSelected = None
        fig11 = pl.figure()
        drawSleepRawCurveWith(self.dStockSleepRaw.values(), fig11, self.rSelected, self.lColors)
        fig11.canvas.mpl_connect('pick_event', self.onPick)
        fig12 = pl.figure()
        drawSleepSectCurveWith(self.dStockSleepRaw.values(), fig12, self.rSelected, self.lColors)
        fig12.canvas.mpl_connect('pick_event', self.onPick)
        fig21 = pl.figure()
        drawFoodDistCurveWith(self.dStockDistRaw.values(), fig21, self.rSelected, self.lColors)
        fig21.canvas.mpl_connect('pick_event', self.onPick)
        fig22 = pl.figure()
        self.llFoodDistRatio = drawFoodDistRatioWith(self.dStockDistRaw.values(), fig22, self.rSelected, self.lColors)
        fig22.canvas.mpl_connect('pick_event', self.onPick)
        drawFoodDistHistogramWith(self.dStockDistRaw.values(), self.rSelected)
        pl.show()

    @staticmethod
    def isNum(s):
        for c in s:
            if c not in '0123456789.':
                return False
        return True

    def onPrintData(self):
        pathOut = os.path.join(self.pathRoot, 'summary')
        if not os.path.exists(pathOut):
            os.mkdir(pathOut)
        self.lbStatusOp['text'] = 'data_table output to ' + pathOut
        batchWriteSleepRawMean(self.dStockSleepRaw.values(), pathOut)
        batchWriteSleepSection(self.dStockSleepRaw.values(), pathOut)
        batchWriteSleepSectionMean(self.dStockSleepRaw.values(), pathOut)
        batchWriteFoodDistCurveMean(self.dStockDistRaw.values(), pathOut)
        writeFoodDistRatio(self.dStockDistRaw.values(), self.llFoodDistRatio, pathOut)

    def onSaveFig(self):
        pathOut = os.path.join(self.pathRoot, 'summary')
        if not os.path.exists(pathOut):
            os.mkdir(pathOut)
        self.lbStatusOp['text'] = 'figures output to ' + pathOut
        fig11 = pl.figure()
        drawSleepRawCurveWith(self.dStockSleepRaw.values(), fig11, self.rSelected, self.lColors)
        fig11.savefig(os.path.join(pathOut, 'sleep_curve_30min.png'))
        fig11.savefig(os.path.join(pathOut, 'sleep_curve_30min.svg'))
        fig12 = pl.figure()
        drawSleepSectCurveWith(self.dStockSleepRaw.values(), fig12, self.rSelected, self.lColors)
        fig12.savefig(os.path.join(pathOut, 'sleep_bar_HalfDay.png'))
        fig12.savefig(os.path.join(pathOut, 'sleep_bar_HalfDay.svg'))
        fig21 = pl.figure()
        drawFoodDistCurveWith(self.dStockDistRaw.values(), fig21, self.rSelected, self.lColors)
        fig21.savefig(os.path.join(pathOut, 'foodDist_curve_30min.png'))
        fig21.savefig(os.path.join(pathOut, 'foodDist_curve_30min.svg'))
        fig22 = pl.figure()
        self.llFoodDistRatio = drawFoodDistRatioWith(self.dStockDistRaw.values(), fig22, self.rSelected, self.lColors)
        fig22.savefig(os.path.join(pathOut, 'foodDistRatio_curve_30min.png'))
        fig22.savefig(os.path.join(pathOut, 'foodDistRatio_curve_30min.svg'))
        drawFoodDistHistogramWith(self.dStockDistRaw.values(), self.rSelected, pathOut)

    def onCloseAll(self):
        pl.close('all')

    def onPick(self, event):
        try:
            stkname = event.artist.get_label()
            self.lbStatusOp['text'] = stkname
            print stkname
        except AttributeError:
            pass


root = tk.Tk()
root.title(u'sleep summariser')
app = Application(master=root)
app.mainloop()
root.destroy()