import os
import time
import smtplib
from email.mime.text import MIMEText
from threading import Thread


def emailProgress(
	content,
	mailto_list=['yzyw0702@163.com'], #receiver
	mail_host="smtp.163.com", #smtp 163 server
	mail_user="yzyw0702@163.com", #user name
	mail_pass="13937161910yw163", #security code
	mail_postfix="163.com" # 163 postfix
):
	me="video convertion report "+"<"+mail_user+"@"+mail_postfix+">"
	msg = MIMEText(content,_subtype='plain')
	msg['Subject'] = 'video convert progress report'
	msg['From'] = me
	msg['To'] = ";".join(mailto_list) #use ';' to separate different eceivers
	try:
		server = smtplib.SMTP()
		server.connect(mail_host) # connect to server
		server.login(mail_user,mail_pass) # login procedure
		server.sendmail(me, mailto_list, msg.as_string())
		server.close()
		return True
	except Exception, e:
		print str(e)
		return False


# demo
# emailProgress('progress report.\n', mailto_list=['zh_ch@126.com'])


def lsClips(rootpath, pattern = '.dav'):
	lClips = []
	for d in os.listdir(rootpath):
		if os.path.isdir(d):
			continue
		if pattern in d:
			lClips.append(os.path.join(rootpath,d))
	return lClips


def getIdx(query, lRef):
	for i, ref in enumerate(lRef):
		if query == ref:
			return i
	return -1


def clearPrvTmpl(rootpath = '.', ptnSrc = '.dav', ptnDst = '.avi'):
	lSrc = lsClips(rootpath, ptnSrc)
	lDst = lsClips(rootpath, ptnDst)
	NDst = len(lDst)
	for i, src in enumerate(lSrc):
		query = src[:-4] + ptnDst
		iDst = getIdx(query, lDst)
		if iDst > -1 and iDst < NDst - 2:
			print 'to remove ' + src
			emailProgress('source = %s\ncurrent_file = %s' % (rootpath, src))
			os.remove(src)
	print 'NSrc=%d, NDst=%d' % (len(lSrc), NDst)
	time.sleep(60)


def testClearPrvTempl(rootpath = os.getcwd()):
	Nsrc = 100
	# generate src files
	for i in range(Nsrc):
		fSrc = os.path.join(rootpath, 'test%d.src' % i)
		hSrc = open(fSrc, 'w')
		hSrc.write('%d.src' % i)
		hSrc.close()
	td = Thread(target= clearPrvTmpl, args = (rootpath, '.src', '.dst',))
	td.start()
	# generate new dst files while clearing previous src files
	for i in range(Nsrc):
		fDst = os.path.join(rootpath, 'test%d.dst' % i)
		hDst = open(fDst, 'w')
		hDst.write('%d.dst' % i)
		hDst.close()
		time.sleep(1)

def launch():
	
	emailProgress('source = ' + os.getcwd())
	while(1):
		clearPrvTmpl(os.getcwd(), '.dav', '.avi')
		#clearPrvTmpl(os.getcwd(), '.src', '.dst')
		



# testClearPrvTempl()
launch()