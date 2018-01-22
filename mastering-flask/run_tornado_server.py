# -*- coding: utf-8 -*-
import os
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from webapp import create_app


# 默认使用 default 配置
flask_app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
tornado_app = WSGIContainer(flask_app)

http_server = HTTPServer(tornado_app)
http_server.listen(5000)
IOLoop.instance().start()
