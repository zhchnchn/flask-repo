# -*- coding: utf-8 -*-
import os
from gevent.wsgi import WSGIServer
from webapp import create_app


# 默认使用 default 配置
app = create_app(os.environ.get('FLASK_CONFIG', 'default'))

server = WSGIServer(('', 5000), app)
server.serve_forever()
