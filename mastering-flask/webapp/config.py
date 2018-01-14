# -*- coding: utf-8 -*-
import os


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
    DEBUG = True
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
    # MongoDB settings
    MONGODB_SETTINGS = {'db': 'local', 'host': 'localhost', 'port': 27017}
