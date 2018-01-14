# -*- coding: utf-8 -*-
from flask import abort
from flask_restful import Resource, fields, marshal_with
from .fields import HTMLField
from ...models import Post

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
            posts = Post.query.all()
            return posts


