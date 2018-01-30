# -*- coding: utf-8 -*-
from flask import jsonify, request, current_app, url_for
from ...models import User, Post
from . import api_blueprint


@api_blueprint.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api_blueprint.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.publish_date.desc()).paginate(
        page,
        per_page=current_app.config['PAGINATION_POST_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page+1, _external=True)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api_blueprint.route('/users/<int:id>/timeline/')
def get_user_following_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.following_posts.order_by(
        Post.publish_date.desc()
    ).paginate(
        page,
        per_page=current_app.config['PAGINATION_POST_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_following_posts', id=id, page=page-1,
                       _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_following_posts', id=id, page=page+1,
                       _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
