# -*- coding: utf-8 -*-
import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # used for WTForms
    SECRET_KEY = 'hard to guess string'


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

