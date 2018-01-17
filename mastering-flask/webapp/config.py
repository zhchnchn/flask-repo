# -*- coding: utf-8 -*-
import os
import datetime

from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # used for WTForms
    SECRET_KEY = 'hard to guess string'
    # used for google reCAPTCHA
    # RECAPTCHA_PUBLIC_KEY = "6LfxDkAUAAAAALj-PpjdEd-zb1MKakbxD776zaAK"
    # RECAPTCHA_PRIVATE_KEY = '6LfxDkAUAAAAAPtAOUGy278uYYwEYp31cmE4QbVg'


class ProductConfig(Config):
    pass


class DevConfig(Config):
    # SERVER_NAME = 'localhost:5000'

    # Debug tool bar extension
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # config.py文件被移动到了app目录下，但我们想将生成的sqlite数据库文件仍然放在外层目录下，
    # 则此处我们必须修改SQLALCHEMY的URL为相对路径。
    # os.path.pardir 返回系统的父目录的表示形式，Linux下为".."
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,
                                                          os.path.pardir,
                                                          'data.sqlite')
    SQLALCHEMY_COMMIT_ON_TERDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 将ORM操作转为对应的SQL语句并显示
    # SQLALCHEMY_ECHO = True

    CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
    # redis://127.0.0.1:6379/1
    CELERY_RESULT_BACKEND = "amqp://guest:guest@localhost:5672//"
    # CELERY_IGNORE_RESULT = False
    CELERYBEAT_SCHEDULE = {
        'log-every-30-seconds': {
            'task': 'webapp.tasks.log',
            'schedule': datetime.timedelta(seconds=30),
            'args': ("Message",)
        },
        # 每周六上午10点执行：crontab(day_of_week=6, hour='10')
        'weekly-digest': {
            'task': 'webapp.tasks.digest',
            'schedule': crontab(minute='*/1')  # test: 每一分钟执行一次
        },
    }

    # Flask-Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = '6379'
    # CACHE_REDIS_PASSWORD = 'password'
    CACHE_REDIS_DB = '0'

