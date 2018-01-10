# -*- coding: utf-8 -*-
from flask import Flask
from controllers.blog import blog_blueprint
from controllers.main import main_blueprint
from models import db
from extensions import bcrypt


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    Arguments:
        object_name: the python path of the config object,
                     e.g. webapp.config.DevConfig
    """

    app = Flask(__name__)
    app.config.from_object(object_name)

    # init SQLAlchemy
    db.init_app(app)
    # init Bcrypt
    bcrypt.init_app(app)

    # register blueprint
    app.register_blueprint(blog_blueprint)
    app.register_blueprint(main_blueprint)

    return app


if __name__ == '__main__':
    app = create_app('webapp.config.DevConfig')
    app.run()
