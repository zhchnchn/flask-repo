# -*- coding: utf-8 -*-
from flask import jsonify, request, g, url_for, current_app
from flask_principal import Permission, UserNeed
from ...models import db, Post
from ...extensions import admin_permission
from . import api_blueprint
from .errors import forbidden


@api_blueprint.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page,
        per_page=current_app.config['PAGINATION_POST_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api_blueprint.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api_blueprint.route('/posts/', methods=['POST'])
def new_post():
    post = Post.from_json(request.json)
    post.user = g.current_user
    db.session.add(post)
    db.session.commit()
    # 响应的主体中包含了
    # 1. 新建的资源，
    # 2. 201状态码，
    # 3. 把Location首部的值设为刚创建的这个资源的URL
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id, _external=True)}


@api_blueprint.route('/posts/<int:id>', methods=['PUT'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    permission = Permission(UserNeed(post.user_id))
    # 除了文章作者，我们希望管理员也可以修改任何文章
    if not permission.can() and not admin_permission.can():
        return forbidden('Insufficient permissions')

    post.title = request.json.get('title', post.title)
    post.text = request.json.get('text', post.text)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
