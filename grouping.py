import os
import shutil

def grouping(rootpath):
	llAvi = []
	lGrps = []
	fTxt = ''
	hTxt = None
	for f in os.listdir(rootpath):
		if '.avi' in f:
			grp = str(int(f.split('-')[0]))
			grp = os.path.join(rootpath, grp)
			if grp not in lGrps:
				lGrps.append(grp)
				os.mkdir(grp)
				llAvi.append([])
				fTxt = os.path.join(grp, 'list.txt')
				if hTxt:
					hTxt.close()
				hTxt = open(fTxt, 'w')
			hTxt.write('%s\n' % f)
			llAvi.append(f)
			shutil.move(f, grp)
	hTxt.close()
	fTxt = os.path.join(rootpath, 'tasklist.txt')
	hTxt = open(fTxt, 'w')
	for grp in lGrps:
		hTxt.write('%s/\n' % grp.split('/')[-1])
	hTxt.close()


grouping('./')