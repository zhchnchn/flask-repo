# -*- coding: utf-8 -*-
import os
from webapp import create_app
# 注意这里导入的是celery包中的Celery类，而不是Flask-Celery-Helper扩展中的Celery类
from celery import Celery
# 必须导入该工作函数，尽管在本文件中没有用到，否则会报下面的错误：
#   Received unregistered task of type 'webapp.tasks.log'.
#   The message has been ignored and discarded.
#   Did you remember to import the module containing this task?
#   Or maybe you're using relative imports?
from webapp.tasks import log


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_BACKEND_URL']
    )

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


env = os.environ.get('WEBAPP_ENV', 'Dev')
flask_app = create_app('webapp.config.%sConfig' % env.capitalize())
celery = make_celery(flask_app)
