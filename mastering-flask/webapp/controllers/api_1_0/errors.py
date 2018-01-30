# -*- coding: utf-8 -*-
from flask import jsonify
from . import api_blueprint
from ...exceptions import ValidationError


def bad_request(message):
    response = jsonify({'error': '400 - bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': '401 - unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': '403 - forbidden', 'message': message})
    response.status_code = 403
    return response


# 创建一个全局异常处理程序, 避免在视图函数中编写捕获异常的代码
@api_blueprint.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
