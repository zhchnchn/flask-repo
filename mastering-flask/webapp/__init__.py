# -*- coding: utf-8 -*-
from flask import Flask
from flask_login import current_user
from flask_principal import identity_loaded, UserNeed, RoleNeed
from controllers.blog import blog_blueprint
from controllers.main import main_blueprint
from controllers.auth import auth_blueprint
from models import db, User, Role, Post, Comment, Tag
from extensions import bcrypt, login_manager, principal, rest_api, \
    debug_toolbar, cache, assets_env, main_css, main_js, admin
from .controllers.rest.auth import AuthApi
from .controllers.rest.post import PostApi
from .controllers.admin import CustomView, CustomModelView, PostView


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
    # init LoginManager
    login_manager.init_app(app)
    # init Principal
    principal.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user object
        identity.user = current_user
        # Add the UserNeed to the identity
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))
        # Add each role to the identity
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    # init DebugToolbarExtension
    debug_toolbar.init_app(app)

    # init Cache
    cache.init_app(app)

    # init Flask-Assets
    assets_env.init_app(app)
    assets_env.register("main_css", main_css)
    assets_env.register("main_js", main_js)

    # init Flask-Admin
    admin.init_app(app)
    admin.add_view(CustomView(name='Custom'))

    models = [User, Role, Comment, Tag]
    for model in models:
        admin.add_view(CustomModelView(model, db.session, category='Models'))
    # 单独处理Post model，因为我们自定了CustomModelView的自类PostView
    admin.add_view(PostView(Post, db.session, category='Models'))

    # init RestApi
    rest_api.add_resource(PostApi, '/api/post', '/api/post/<int:post_id>',
                          endpoint='api')
    rest_api.add_resource(AuthApi, '/api/auth')
    rest_api.init_app(app)

    # register blueprint
    app.register_blueprint(blog_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    return app


if __name__ == '__main__':
    app = create_app('webapp.config.DevConfig')
    app.run()
