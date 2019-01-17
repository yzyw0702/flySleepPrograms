import smtplib
from email.mime.text import MIMEText


def emailProgress(
	content,
	mailto_list=['yzyw0702@163.com'], #receiver
	mail_host="smtp.163.com", #smtp 163 server
	mail_user="yzyw0702@163.com", #user name
	mail_pass="13937161910yw163", #security code
	mail_postfix="163.com" # 163 postfix
):
	me="sleep program report "+"<"+mail_user+"@"+mail_postfix+">"
	msg = MIMEText(content,_subtype='plain')
	msg['Subject'] = 'sleep program progress report'
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