# -*- coding: utf-8 -*-
import os
from webapp import create_app


# 默认使用 default 配置
application = create_app(os.environ.get('FLASK_CONFIG', 'default'))
