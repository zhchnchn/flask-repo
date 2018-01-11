# -*- coding: utf-8 -*-
import datetime
import os

from flask import render_template, redirect, url_for, Blueprint
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from ..models import db, Post, Tag, posts_tags_table, Comment, User
from ..forms import CommentForm, PostForm

blog_blueprint = Blueprint('blog', __name__,
                           # template_folder='../templates/blog'
                           template_folder=os.path.join(
                               os.path.pardir, 'templates', 'blog'),
                           url_prefix='/blog')


def sidebar_data():
    """侧边栏函数
    每个页面都有一个侧边栏，显示5篇最新的文章，以及5个最常用的标签
    """

    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    # 下面的查询对应的SQL语句为
    # SELECT tags.id AS tags_id, tags.title AS tags_title,
    #        count(posts_tags.post_id) AS total
    # FROM tags JOIN posts_tags
    # ON tags.id = posts_tags.tag_id
    # GROUP BY tags.id, tags.title
    # ORDER BY total DESC
    # LIMIT ? OFFSET ?
    top_tags = db.session.query(
        Tag, func.count(posts_tags_table.c.post_id).label('total')
    ).join(posts_tags_table).group_by(Tag).order_by(desc('total')).limit(5).all()

    return recent, top_tags


@blog_blueprint.route('/')
@blog_blueprint.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template('home.html', posts=posts, recent=recent,
                           top_tags=top_tags)


@blog_blueprint.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        new_comment.date = datetime.datetime.now()

        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post', post_id=post_id))

    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('post.html', post=post, tags=tags, comments=comments,
                           recent=recent, top_tags=top_tags, form=form)


@blog_blueprint.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(form.title.data)
        new_post.text = form.text.data
        new_post.publish_date = datetime.datetime.now()
        new_post.user = User.query.filter_by(
            username=current_user.username).one()

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('.post', post_id=new_post.id))

    return render_template('new_post.html', form=form)


@blog_blueprint.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.text = form.text.data
        post.publish_date = datetime.datetime.now()

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('.post', post_id=post.id))

    form.text.data = post.text
    return render_template('edit_post.html', form=form, post=post)


@blog_blueprint.route('/tag/<string:tag_name>')
def tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('tag.html', tag=tag, posts=posts, recent=recent,
                           top_tags=top_tags)


@blog_blueprint.route('/user/<string:username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('user.html', user=user, posts=posts, recent=recent,
                           top_tags=top_tags)
