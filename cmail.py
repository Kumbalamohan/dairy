
import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('kumbalamohankrishna35@gmail.com ','fkdv mgvc ukkr vxbc')
    msg=EmailMessage()
    msg['From']='kumbalamohankrishna35@gmail.com'
    msg['Subject']=subject
    msg['To']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit()

    
