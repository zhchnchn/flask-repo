# -*- coding: utf-8 -*-
import time
import smtplib
from email.mime.text import MIMEText
from .extensions import celery
from .controllers.blog import digest_func


@celery.task()
def log(msg):
    print('log msg start')
    time.sleep(5)
    print('log msg succeed')

    return msg


@celery.task()
def multiply(x, y):
    return x * y


@celery.task(
    bind=True,
    ignore_result=True,
    default_retry_delay=300,
    max_retries=5
)
def digest(self):
    mail_host = "smtp.163.com"     # 使用的邮箱的smtp服务器地址，这里是163的smtp地址
    mail_user = "xxx@163.com"      # 用户名
    mail_pass = "xxx"              # 密码
    mailto_list = ["xxx@qq.com"]   # 收件人(列表)

    msg = MIMEText(digest_func(), 'html')
    # print(msg)
    msg['Subject'] = "Weekly Digest"
    msg['From'] = mail_user
    msg['To'] = ';'.join(mailto_list)  # 将收件人列表以‘;’分隔

    try:
        smtp_server = smtplib.SMTP(mail_host)
        # smtp_server.starttls()
        smtp_server.login(mail_user, mail_pass)
        smtp_server.sendmail(mail_user, mailto_list, msg.as_string())
        smtp_server.close()
        return
    except Exception, e:
        self.retry(exc=e)
