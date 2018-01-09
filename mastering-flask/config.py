# -*- coding: utf-8 -*-


import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    pass


class ProductConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_COMMIT_ON_TERDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

