# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for
from config import DevConfig
from controllers.blog import blog_blueprint
from controllers.main import main_blueprint
from models import db


app = Flask(__name__)
app.config.from_object(DevConfig)

db.init_app(app)


app.register_blueprint(blog_blueprint)
app.register_blueprint(main_blueprint)


if __name__ == '__main__':
    app.run()
