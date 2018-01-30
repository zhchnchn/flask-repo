# -*- coding: utf-8 -*-
from flask import render_template, request, jsonify
from . import blog_blueprint


@blog_blueprint.app_errorhandler(403)
def forbidden(e):
    # 检查Accept请求首部（Werkzeug将其解码为request.accept_mimetypes）
    # 根据首部的值决定客户端期望接收的响应格式
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': '403 - forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403


@blog_blueprint.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': '404 - page not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@blog_blueprint.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': '500 - internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
