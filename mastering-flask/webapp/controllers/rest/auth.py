# -*- coding: utf-8 -*-
from flask import abort
from flask_restful import Resource
from .parsers import user_post_parser
from ...models import User


class AuthApi(Resource):
    def post(self):
        args = user_post_parser.parse_args()
        user = User.query.filter_by(username=args['username']).first()
        if user.check_password(args['password']):
            token = user.generate_auth_token()
            return {'token': token}

        return abort(401)
