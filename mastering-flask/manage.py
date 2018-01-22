# -*- coding: utf-8 -*-
import os
import random
import datetime
from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from flask_migrate import Migrate, MigrateCommand
from webapp import create_app
from webapp.models import db, User, Post, Tag, Comment, Role


# 默认使用 default 配置
app = create_app(os.environ.get('FLASK_CONFIG', 'default'))

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('server', Server())
manager.add_command('showurls', ShowUrls())
manager.add_command('clean', Clean())
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Post=Post, Tag=Tag, Comment=Comment,
                Role=Role)


@manager.command
def insert_data():
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
    admin.set_password("admin")
    admin.roles.append(role_admin)
    admin.roles.append(role_poster)
    admin.roles.append(role_default)
    db.session.add(admin)

    user01 = User(username='user01')
    user01.set_password('test01')
    user01.roles.append(role_poster)
    user01.roles.append(role_default)
    db.session.add(user01)

    user02 = User(username='user02')
    user02.set_password('test02')
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
    manager.run()
