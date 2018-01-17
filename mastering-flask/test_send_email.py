# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText


def send_mail():
    mail_host = "smtp.163.com"      # 使用的邮箱的smtp服务器地址，这里是163的smtp地址
    mail_user = "xxx@163.com"       # 用户名
    mail_pass = "xxx"               # 密码
    mailto_list = ["xxx@qq.com"]  # 收件人(列表)

    content = "电话是XXX"
    msg = MIMEText(content, _subtype='plain')
    msg['Subject'] = "Weekly Digest"
    msg['From'] = mail_user
    msg['To'] = ';'.join(mailto_list)  # 将收件人列表以‘;’分隔

    try:
        smtp_server = smtplib.SMTP(mail_host)
        smtp_server.starttls()
        smtp_server.login(mail_user, mail_pass)
        smtp_server.sendmail(mail_user, mailto_list, msg.as_string())
        smtp_server.close()
        return
    except Exception, e:
        print e.message

if __name__ == '__main__':
    send_mail()
