# -*- coding: utf-8 -*-
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ...models import User, AnonymousUser
from . import api_blueprint
from .errors import unauthorized, forbidden


# 初始化Flask-HTTPAuth
auth = HTTPBasicAuth()


# 在回调函数中验证密令
# 第一个认证参数可以是username或认证令牌。如果这个参数为空，那就假定是匿名用户。
# 如果密码为空，那就假定username_or_token参数提供的是令牌，按照令牌的方式进行认证。
# 如果两个参数都不为空，假定使用常规的username和密码进行认证。
# 在这种实现方式中，基于令牌的认证是可选的，由客户端决定是否使用。
# 为了让视图函数能区分这两种认证方法，我们添加了g.token_used变量。
@auth.verify_password
def verify_password(username_or_token, password):
    if username_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token).first()
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


# 添加到before_request处理程序上的认证机制也会用在这个路由上,
# 为了避免客户端使用旧令牌申请新令牌，要在视图函数中检查g.token_used变量的值，
# 如果使用token请求生成token，就拒绝请求
@api_blueprint.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(),
                    'expiration': 600})
