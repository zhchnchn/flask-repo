# -*- coding: utf-8 -*-
import random
import datetime
from flask import Flask
from webapp.models import User, Tag, Post, db, Role
from webapp.config import config


# 解决如下错误:
# No application found. Either work inside a view function or push an application context.
# https://stackoverflow.com/questions/24060553/creating-a-database-outside-the-application-context
# 由于该模块是独立运行的，而db.session需要在Flask的应用上下文中才能执行，
# 所以我们首先创建了一个Flask app, 然后使用该app的应用上下文
app = Flask(__name__)
app.config.from_object(config['default'])
db.init_app(app)


def insert_data():
    with app.app_context():
        # 不需要在这里创建库，应该使用数据库升级命令`db upgrade`来创建库
        # db.create_all()

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

        # add User
        admin = User(username='admin')
        admin.email = 'admin@163.com'
        admin.password = 'admin'
        admin.confirmed = True
        admin.roles.append(role_admin)
        admin.roles.append(role_poster)
        admin.roles.append(role_default)
        db.session.add(admin)

        user01 = User(username='user01')
        user01.email = 'user01@163.com'
        user01.password = 'test01'
        user01.confirmed = True
        user01.roles.append(role_poster)
        user01.roles.append(role_default)
        db.session.add(user01)

        user02 = User(username='user02')
        user02.email = 'user02@163.com'
        user02.password = 'test02'
        user02.confirmed = True
        user02.roles.append(role_poster)
        user02.roles.append(role_default)
        db.session.add(user02)

        # add Tag and Post
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


if __name__ == '__main__':
    insert_data()
