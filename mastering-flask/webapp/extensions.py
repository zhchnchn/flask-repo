# -*- coding: utf-8 -*-
"""
用来保存将会用到的所有扩展
"""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed


########################## Flask-Bcrypt extension #########################

bcrypt = Bcrypt()


########################## Flask-Login extension ##########################

login_manager = LoginManager()

# settings
login_manager.login_view = 'auth.login'  # the Blueprint endpoint of login
login_manager.session_protection = 'strong'
login_manager.login_message = 'Please login to access this page'
login_manager.login_message_category = 'info'


# return a User object
@login_manager.user_loader
def load_user(userid):
    from models import User
    return User.query.get(userid)


########################## Flask-Principal extension ##########################

principal = Principal()

admin_permission = Permission(RoleNeed('admin'))
poster_permission = Permission(RoleNeed('poster'))
default_permission = Permission(RoleNeed('default'))
