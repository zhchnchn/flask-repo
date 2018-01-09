# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for
from config import DevConfig
from controllers.blog import blog_blueprint
from models import db


app = Flask(__name__)
app.config.from_object(DevConfig)

db.init_app(app)


@app.route('/')
def index():
    """由于蓝图添加了URL前缀，因此在基础app对象上已经没有任何视图了，访问网站的根路径，
    将没有对应的视图函数，因此在根路径上加一个重定向
    """
    return redirect(url_for('blog.home'))


app.register_blueprint(blog_blueprint)


if __name__ == '__main__':
    app.run()
