# -*- coding: utf-8 -*-
import datetime
import hashlib
import random
from flask import current_app, request
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


# follows table
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                            primary_key=True)
    following_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    # 添加email字段，用户也可以使用电子邮件地址登录
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    confirmed = db.Column(db.Boolean, default=False)
    # add User information column
    name = db.Column(db.String(64))
    location = db.Column(db.String(255))
    about_me = db.Column(db.Text())
    register_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    # 把email的MD5散列值保存在数据库
    gravatar_hash = db.Column(db.String(32))
    # relations
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users_table,
                            backref=db.backref('users', lazy='dynamic'))
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    # 关注别人的一对多关系，多的一方为Follow模型
    followings = db.relationship(
        'Follow',
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    # 被别人关注的一对多关系，，多的一方为Follow模型
    followers = db.relationship(
        'Follow',
        foreign_keys=[Follow.following_id],
        backref=db.backref('following', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __init__(self, username):
        self.username = username
        # 由于email的MD5散列值是不变的，因此可以事前计算,将其缓存在User模型中
        if self.email is not None and self.gravatar_hash is None:
            self.gravatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

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

    def generate_reset_token(self, email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id, 'email': email})

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

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.gravatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()

        return True

    # 用户每次访问网站后，last_seen这个值都会被刷新
    def update_last_seen(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://s.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash_val = self.gravatar_hash or \
                   hashlib.md5(self.email.encode('utf-8')).hexdigest()

        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash_val, size=size, default=default, rating=rating)

    @property
    def following_posts(self):
        return Post.query.join(
            Follow, Follow.following_id == Post.user_id
        ).filter(Follow.follower_id == self.id)

    # 生成模拟数据
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        # 设定一个admin用户和2个普通账户，以方便使用密码登录
        admin = User(username='admin')
        admin.email = 'admin@163.com'
        admin.password = 'admin'
        admin.confirmed = True
        admin.name = forgery_py.name.full_name()
        admin.location = forgery_py.address.city()
        admin.about_me = forgery_py.lorem_ipsum.sentence()
        admin.register_time = forgery_py.date.date(True)
        admin.roles.append(Role.query.filter_by(name='admin').first())
        admin.roles.append(Role.query.filter_by(name='poster').first())
        admin.roles.append(Role.query.filter_by(name='default').first())
        db.session.add(admin)
        user01 = User(username='user01')
        user01.email = 'user01@163.com'
        user01.password = 'user01'
        user01.confirmed = True
        user01.name = forgery_py.name.full_name()
        user01.location = forgery_py.address.city()
        user01.about_me = forgery_py.lorem_ipsum.sentence()
        user01.register_time = forgery_py.date.date(True)
        user01.roles.append(Role.query.filter_by(name='poster').first())
        user01.roles.append(Role.query.filter_by(name='default').first())
        db.session.add(user01)
        user02 = User(username='user02')
        user02.email = 'user02@163.com'
        user02.password = 'user02'
        user02.confirmed = True
        user02.name = forgery_py.name.full_name()
        user02.location = forgery_py.address.city()
        user02.about_me = forgery_py.lorem_ipsum.sentence()
        user02.register_time = forgery_py.date.date(True)
        user02.roles.append(Role.query.filter_by(name='poster').first())
        user02.roles.append(Role.query.filter_by(name='default').first())
        db.session.add(user02)
        db.session.commit()

        random.seed()
        for i in xrange(count-3):
            u = User(username=forgery_py.internet.user_name(True))
            u.email = forgery_py.internet.email_address()
            u.password = forgery_py.lorem_ipsum.word()
            u.confirmed = True
            u.name = forgery_py.name.full_name()
            u.location = forgery_py.address.city()
            u.about_me = forgery_py.lorem_ipsum.sentence()
            u.register_time = forgery_py.date.date(True)
            u.roles.append(Role.query.filter_by(name='poster').first())
            u.roles.append(Role.query.filter_by(name='default').first())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def is_following(self, user):
        return self.followings.filter_by(
            following_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(following=user, follower=self)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followings.filter_by(following_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    @staticmethod
    def generate_fake():
        # 这里设定了3种角色
        role_admin = Role(name='admin')
        role_admin.description = "administrator role"
        role_poster = Role(name='poster')
        role_poster.description = "the registered user role"
        role_default = Role(name='default')
        role_default.description = 'the unregistered user role'
        db.session.add(role_admin)
        db.session.add(role_poster)
        db.session.add(role_default)
        db.session.commit()


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(
        db.DateTime(), index=True, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=posts_tags_table,
                           backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

    @staticmethod
    def generate_fake(count=100):
        import forgery_py

        random.seed()
        user_count = User.query.count()
        tag_list = Tag.query.all()
        for i in xrange(count):
            u = User.query.offset(random.randint(0, user_count-1)).first()
            tags = random.sample(tag_list, random.randint(1, 3))
            p = Post(title=forgery_py.lorem_ipsum.title())
            p.text = forgery_py.lorem_ipsum.sentences(random.randint(1, 5))
            p.publish_date = forgery_py.date.date(True)
            p.user = u
            p.tags = tags
            db.session.add(p)

        db.session.commit()


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime(), index=True, default=datetime.datetime.utcnow)
    disabled = db.Column(db.Boolean())  # 查禁不当评论
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer(), db.ForeignKey('posts.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])

    @staticmethod
    def generate_fake(count=100):
        import forgery_py

        random.seed()
        post_count = Post.query.count()
        for i in xrange(count):
            post = Post.query.offset(random.randint(0, post_count - 1)).first()
            c = Comment(name=forgery_py.lorem_ipsum.title())
            c.text = forgery_py.lorem_ipsum.sentences(random.randint(1, 5))
            c.date = forgery_py.date.date(True)
            c.post = post
            db.session.add(c)

        db.session.commit()


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)

    @staticmethod
    def generate_fake(count=10):
        from random import seed
        import forgery_py

        seed()
        for i in xrange(count):
            t = Tag(title=forgery_py.lorem_ipsum.word())
            db.session.add(t)

        db.session.commit()
