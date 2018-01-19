# -*- coding: utf-8 -*-
import os
from gevent.wsgi import WSGIServer
from webapp import create_app


# 默认使用 Dev 配置
env = os.environ.get('WEBAPP_ENV', 'Dev')
app = create_app('webapp.config.{}Config'.format(env.capitalize()))

server = WSGIServer(('', 5000), app)
server.serve_forever()
