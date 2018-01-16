# -*- coding: utf-8 -*-
import time

from .extensions import celery


@celery.task()
def log(msg):
    print('log msg start')
    time.sleep(5)
    print('log msg succeed')

    return msg


@celery.task()
def multiply(x, y):
    return x * y
