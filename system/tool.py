#-*- coding: utf-8 -*-
from email.MIMEText import MIMEText
import smtplib
import settings

def send_mail(mail_to, subject, msg_txt):
    # Record the MIME types of both parts - text/plain and text/html.
    msg = MIMEText(msg_txt, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = settings.MAIL_FROM
    msg['To'] = mail_to
    
    server = smtplib.SMTP(settings.SMTP_SERVER, 25)

    #try:
    server.login(settings.MAIL_FROM, settings.MAIL_PW)
    mailto_list = mail_to.strip().split(",")
    if len(mailto_list) > 1:
        for mailtoi in mailto_list:
            server.sendmail(settings.MAIL_FROM, mailtoi.strip(), msg.as_string())
    else:
        server.sendmail(settings.MAIL_FROM, mail_to, msg.as_string())
    #except:
        #server.quit()
        #return False

    server.quit()
    return True