# -*- coding: utf-8 -*-
import os
import datetime
import tempfile

from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # used for WTForms
    SECRET_KEY = 'hard to guess string'
    # used for google reCAPTCHA
    # RECAPTCHA_PUBLIC_KEY = "6LfxDkAUAAAAALj-PpjdEd-zb1MKakbxD776zaAK"
    # RECAPTCHA_PRIVATE_KEY = '6LfxDkAUAAAAAPtAOUGy278uYYwEYp31cmE4QbVg'

    # 配置侧边栏显示最新发布的文章，以及最常用的标签的个数
    TOP_POSTS_NUM = 10
    TOP_TAGS_NUM = 10
    # 分页，每页显示的文章数
    PAGINATION_PER_PAGE = 10


class ProductConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,
                                                          os.path.pardir,
                                                          'data-product.sqlite')
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
                                                          'data-dev.sqlite')
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
    # 当使用的缓存类型为null时，不让抛出警告信息
    CACHE_NO_NULL_WARNING = True

    # Flask-Assets
    # 在开发环境中不要编译库文件
    ASSETS_DEBUG = True

    # Flask-Mail
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USERNAME = 'xxx@163.com'
    MAIL_PASSWORD = 'xxx'
    MAIL_SUBJECT_PREFIX = '[Blog]'
    MAIL_SENDER = 'Blog Admin <xxx@163.com>'


class TestConfig(Config):
    db_file = tempfile.NamedTemporaryFile()

    DEBUG = True
    # 关闭Flask Debugtoolbar
    DEBUG_TB_ENABLED = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_file.name
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
    CELERY_BACKEND_URL = "amqp://guest:guest@localhost:5672//"

    CACHE_TYPE = 'null'
    # 当使用的缓存类型为null时，不让抛出警告信息
    CACHE_NO_NULL_WARNING = True

    # WTForms不进行CSRF检查
    WTF_CSRF_ENABLED = False

    # Flask_Assets
    # 在测试环境中不要编译库文件
    ASSETS_DEBUG = True


config = {
    'dev': DevConfig,
    'test': TestConfig,
    'product': ProductConfig,
    'default': DevConfig
}
