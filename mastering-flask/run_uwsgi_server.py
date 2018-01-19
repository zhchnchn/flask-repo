# -*- coding: utf-8 -*-
import os
from webapp import create_app


# 默认使用 Dev 配置
env = os.environ.get('WEBAPP_ENV', 'Dev')
application = create_app('webapp.config.{}Config'.format(env.capitalize()))
