# -*- coding: utf-8 -*-
from flask import abort
from flask_restful import Resource, fields, marshal_with
from .fields import HTMLField
from .parsers import post_get_parser
from ...models import Post, User, Tag

nested_tag_fields = {
    'id': fields.Integer(),
    'title': fields.String()
}

post_fields = {
    'author': fields.String(attribute=lambda x: x.user.username),
    'title': fields.String(),
    'text': HTMLField(),
    'publish_date': fields.DateTime(dt_format='iso8601'),
    'tags': fields.List(fields.Nested(nested_tag_fields))
}


class PostApi(Resource):
    @marshal_with(post_fields)
    def get(self, post_id=None):
        if post_id:
            post = Post.query.get(post_id)
            if not post:
                abort(404)
            return post
        else:
            args = post_get_parser.parse_args()
            page = args['page'] or 1

            if args['user']:
                user = User.query.filter_by(username=args['user']).first()
                if not user:
                    abort(404)

                posts = user.posts.order_by(
                    Post.publish_date.desc()).paginate(page, 30)
            else:
                posts = Post.query.order_by(
                    Post.publish_date.desc()).paginate(page, 30)

            return posts.items


