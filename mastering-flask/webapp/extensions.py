# -*- coding: utf-8 -*-
"""
用来保存将会用到的所有扩展
"""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed
from flask_restful import Api
from flask_celery import Celery
from flask_debugtoolbar import DebugToolbarExtension
from flask_cache import Cache
from flask_assets import Environment, Bundle
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_mail import Mail


# ******************* Flask-Bcrypt extension ********************************* #

bcrypt = Bcrypt()


# ******************* Flask-Login extension ********************************** #

login_manager = LoginManager()

# settings
login_manager.login_view = 'auth.login'  # the Blueprint endpoint of login
login_manager.session_protection = 'strong'
login_manager.login_message = 'Please login to access this page'
login_manager.login_message_category = 'info'


# 加载用户的回调函数load_user, 接收以Unicode字符串形式表示的用户标识符
#
@login_manager.user_loader
def load_user(userid):
    from models import User
    # 字符串userid转为int再查询
    return User.query.get(int(userid))


# ******************* Flask-Principal extension ****************************** #

principal = Principal()
# 这里设定了3种权限, 这些权限会被绑定到 Identity 之后才会发挥作用.
admin_permission = Permission(RoleNeed('admin'))
poster_permission = Permission(RoleNeed('poster'))
default_permission = Permission(RoleNeed('default'))


# ******************* Flask-Restful extension ******************************** #

rest_api = Api()


# ******************* Flask-Celery-Helper extension ************************** #

celery = Celery()


# ******************* Flask-DebugToolbarExtension extension ****************** #

debug_toolbar = DebugToolbarExtension()


# ******************* Flask-Cache extension ********************************** #

cache = Cache()


# ******************* Flask-Assets extension ********************************* #

assets_env = Environment()

main_css = Bundle(
    'css/bootstrap.min.css',
    filters='cssmin',
    output='css/common.css'
)

main_js = Bundle(
    'js/jquery.min.js',
    'js/bootstrap.min.js',
    filters='jsmin',
    output='js/common.js'
)


# ******************* Flask-Admin extension ********************************** #

admin = Admin()


# ******************* Flask-Bootstrap extension ********************************** #

bootstrap = Bootstrap()


# ******************* Flask-Mail extension ********************************* #

mail = Mail()
