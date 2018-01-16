# -*- coding: utf-8 -*-
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from flask import render_template
from .extensions import celery
from .models import Post


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
    # 找出这周的起始和结束日
    # 取出当前时间的年，周
    year, week = datetime.datetime.now().isocalendar()[0:2]
    # date赋值为当年的1月1号
    date = datetime.date(year, 1, 1)
    # date.weekday()：判断当年的1月1号是周几，如果是周一，则为0，周二为1，以此类推
    # 如果当年的1月1号>3，即为周五或周六或周日，则日期加上该周剩余的几天，即当年的1月1号所在的周
    #  划归为上一年。
    # 如果当年的1月1号<=3，则日期减去这几天，即将上一年的几天也算作该周。
    # 从而得到当年的第一周的起始日期，赋给date变量
    if date.weekday() > 3:
        date = date + datetime.timedelta(7 - date.weekday())
    else:
        date = date - datetime.timedelta(date.weekday())
    # delta为当前时间所在的周数(week)减一，乘以7，得到总天数
    delta = datetime.timedelta(days=(week - 1) * 7)
    # 日期加上一个间隔,返回一个新的日期对象，days=6 表示周日
    start, end = date + delta, date + delta + datetime.timedelta(days=6)

    posts = Post.query.filter(
        Post.publish_date >= start,
        Post.publish_date <= end
    ).all()
    print("length of posts: %d" % len(posts))
    if len(posts) == 0:
        return

    mail_host = "smtp.163.com"  # 使用的邮箱的smtp服务器地址，这里是163的smtp地址
    mail_user = "xxx@163.com"  # 用户名
    mail_pass = "xxx"  # 密码
    mailto_list = ["xxx@qq.com", ]  # 收件人(列表)

    msg = MIMEText(render_template("digest.html", posts=posts), 'html')
    print(msg)
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
        self.retry(exc=e)
