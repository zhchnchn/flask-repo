# -*- coding: utf-8 -*-
import datetime
import os

from flask import render_template, redirect, url_for, Blueprint, abort
from flask_login import login_required, current_user
from flask_principal import Permission, UserNeed
from sqlalchemy import func, desc
from ..models import db, Post, Tag, posts_tags_table, Comment, User
from ..forms import CommentForm, PostForm
from ..extensions import admin_permission, poster_permission, cache

blog_blueprint = Blueprint('blog', __name__,
                           # template_folder='../templates/blog'
                           template_folder=os.path.join(
                               os.path.pardir, 'templates', 'blog'),
                           url_prefix='/blog')

@cache.cached(timeout=7200, key_prefix='sidebar_data')
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
@cache.cached(timeout=60)
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template('home.html', posts=posts, recent=recent,
                           top_tags=top_tags)


@blog_blueprint.route('/post/<int:post_id>', methods=['GET', 'POST'])
@cache.cached(timeout=60)
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
@poster_permission.require(http_exception=403)
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
@poster_permission.require(http_exception=403)
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    permission = Permission(UserNeed(post.user_id))
    # 除了文章作者，我们希望管理员也可以修改任何文章
    if permission.can() or admin_permission.can():
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

    # 如果没有权限，直接返回403错误
    abort(403)


@blog_blueprint.route('/tag/<string:tag_name>')
@cache.cached(timeout=60)
def tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('tag.html', tag=tag, posts=posts, recent=recent,
                           top_tags=top_tags)


@blog_blueprint.route('/user/<string:username>')
@cache.cached(timeout=60)
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('user.html', user=user, posts=posts, recent=recent,
                           top_tags=top_tags)


@blog_blueprint.route('/digest')
@cache.cached(timeout=60)
def digest_func():
    # 找出这周的起始和结束日
    # 取出当前时间的年，周
    year, week = datetime.datetime.now().isocalendar()[0:2]
    # date赋值为当年的1月1号
    date = datetime.date(year, 1, 1)
    # date.weekday()：判断当年的1月1号是周几，如果是周一，则为0，周二为1，以此类推
    # 如果当年的1月1号>3，即为周五或周六或周日，则日期加上该周剩余的几天，即当年的1月1号所在的周
    #  划归为上一年。
    # 如果当年的1月1号<=3，则日期减去这几天，即将上一年的几天也算作该周。
    # 从而得到当年的第一周的起始日期，赋给date变量
    if date.weekday() > 3:
        date = date + datetime.timedelta(7 - date.weekday())
    else:
        date = date - datetime.timedelta(date.weekday())
    # delta为当前时间所在的周数(week)减一，乘以7，得到总天数
    delta = datetime.timedelta(days=(week - 1) * 7)
    # 日期加上一个间隔,返回一个新的日期对象，days=6 表示周日
    start, end = date + delta, date + delta + datetime.timedelta(days=6)

    posts = Post.query.filter(
        Post.publish_date >= start,
        Post.publish_date <= end
    ).all()

    if len(posts) == 0:
        return None

    return render_template("digest.html", posts=posts)

