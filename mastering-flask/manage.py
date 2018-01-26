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

    # 注意调用顺序
    Role.generate_fake()
    User.generate_fake()
    Tag.generate_fake()
    Post.generate_fake()
    Comment.generate_fake()


@manager.command
def clear_data():
    db.engine.execute("delete from roles;")
    db.engine.execute("delete from users;")
    db.engine.execute("delete from posts;")
    db.engine.execute("delete from tags;")
    db.engine.execute("delete from comments;")
    db.engine.execute("delete from posts_tags;")
    db.engine.execute("delete from roles_users;")
    db.session.commit()


@manager.command
def test():
    """Run the unit tests in the tests/unit folder."""
    import unittest
    tests = unittest.TestLoader().discover('tests/unit')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
