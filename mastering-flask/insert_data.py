# -*- coding: utf-8 -*-
import random
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from webapp.models import User, Tag, Post, db, Role


# create app
app = Flask(__name__)
app.config.from_object('webapp.config.DevConfig')
db.init_app(app)

# Resolve the error: No application found. Either work inside a view function or push an application context.'
# https://stackoverflow.com/questions/24060553/creating-a-database-outside-the-application-context
with app.app_context():

    # add User
    user01 = User(username='user01')
    user01.set_password('test01')
    db.session.add(user01)

    user02 = User(username='user02')
    user02.set_password('test02')
    db.session.add(user02)

    db.session.commit()

    # add Post ang Tag
    user01 = User.query.filter_by(username='user01').first()
    user02 = User.query.filter_by(username='user02').first()
    tag_one = Tag('Python')
    tag_two = Tag('Flask')
    tag_three = Tag('SQLAlechemy')
    tag_four = Tag('Jinja')
    tag_list = [tag_one, tag_two, tag_three, tag_four]
    s = "Example Text"

    for i in xrange(1, 101):
        new_post = Post("Post {}".format(i))
        if i % 2:
            new_post.user = user01
        else:
            new_post.user = user02
        new_post.publish_date = datetime.datetime.now()
        new_post.text = s
        new_post.tags = random.sample(tag_list, random.randint(1, 3))
        db.session.add(new_post)

    db.session.commit()

    # add Role
    user01 = User.query.filter_by(username='user01').first()
    user02 = User.query.filter_by(username='user02').first()
    # 这里设定了3种角色
    role_admin = Role(name='admin')
    role_poster = Role(name='poster')
    role_default = Role(name='default')
    role_admin.users = [user01]
    role_poster.users = [user02]
    db.session.add(role_admin)
    db.session.add(role_poster)
    db.session.add(role_default)

    db.session.commit()

