# -*- coding: utf-8 -*-
from flask_httpauth import HTTPBasicAuth
from ...models import User
from . import api_blueprint
from .errors import unauthorized, forbidden


# 初始化Flask-HTTPAuth
auth = HTTPBasicAuth()


# 在回调函数中验证密令
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        #
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.check_password(password)


# Flask-HTTPAuth错误处理程序
@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


# 在before_request处理程序中进行认证，则api_blueprint中的所有路由都能进行自动认证
@api_blueprint.before_request
@auth.login_required
def before_request():
    # 对非匿名用户，如果还没有确认账户，则不通过认证
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

