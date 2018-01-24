# -*- coding: utf-8 -*-
from flask import current_app
from flask_login import UserMixin
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


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    # 添加email字段，用户也可以使用电子邮件地址登录
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users_table,
                            backref=db.backref('users', lazy='dynamic'))
    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return "<User, '{}'>".format(self.username)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

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

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('confirm') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        db.session.commit()

        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('reset') != self.id:
            return False

        self.password = new_password
        db.session.add(self)
        db.session.commit()

        return True


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
