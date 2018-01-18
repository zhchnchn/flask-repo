# -*- coding: utf-8 -*-
from flask import current_app
from flask_login import AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy
from extensions import bcrypt, cache
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, \
    SignatureExpired, BadSignature


db = SQLAlchemy()


# posts_tags_table
posts_tags_table = db.Table(
    'posts_tags',
    db.Column('post_id', db.Integer(), db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tags.id'))
)


# roles_users_table
roles_users_table = db.Table(
    'roles_users',
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')),
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id'))
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users_table,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return "<User, '{}'>".format(self.username)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @property
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        return False

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    @cache.memoize(timeout=60)
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user = User.query.get(data['id'])
        return user


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=posts_tags_table,
                           backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('posts.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)
