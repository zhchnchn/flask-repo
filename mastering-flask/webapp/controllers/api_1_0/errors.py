# -*- coding: utf-8 -*-
from flask import jsonify
from . import api_blueprint


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

