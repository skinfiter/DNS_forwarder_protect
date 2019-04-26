# encoding=utf-8

from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import *


def send_mail(tittle,html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = tittle
    msg['From'] = send_mail_info['From']
    msg['To']=send_mail_info["To"][0]
    part=MIMEText(html,'html','utf-8')
    msg.attach(part)
    try:
        s=SMTP('smtp.exmail.qq.com')
        s.login(send_mail_info["user"], send_mail_info["passwd"])
        s.sendmail(send_mail_info['From'],send_mail_info["To"],msg.as_string())
        s.quit()
        print 'mail sent'
    except Exception, e:
        print 'mail not sent'
        print Exception, e



if __name__=="__main__":
    send_mail(title,"hello song!")