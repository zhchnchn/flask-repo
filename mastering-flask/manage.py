# -*- coding: utf-8 -*-
import os
from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from flask_migrate import Migrate, MigrateCommand
from webapp import create_app
from webapp.models import db, User, Post, Tag, Comment, Role, Follow

# 保证在全局作用域中的所有代码执行之前，启动覆盖检测
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='webapp/*')
    COV.start()

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
                Role=Role, Follow=Follow)


@manager.command
def insert_data():
    # 不需要在这里创建库，应该使用数据库升级命令`db upgrade`来创建库
    # db.create_all()

    # 注意调用顺序
    Role.generate_fake()
    User.generate_fake()
    Tag.generate_fake()
    Post.generate_fake()
    Comment.generate_fake(1000)


@manager.command
def clear_data():
    db.engine.execute("delete from roles;")
    db.engine.execute("delete from users;")
    db.engine.execute("delete from posts;")
    db.engine.execute("delete from tags;")
    db.engine.execute("delete from comments;")
    db.engine.execute("delete from posts_tags;")
    db.engine.execute("delete from roles_users;")
    db.engine.execute("delete from follows;")
    db.session.commit()


# test命令添加coverage参数,Flask-Script根据参数名确定选项名，并据此向函数中传入True或False
# 调用参数的方法： python manage.py test --coverage
@manager.command
def test(coverage=False):
    """Run the unit tests in the tests/unit folder."""
    # 如果没有设置环境变量，则先设定环境变量FLASK_COVERAGE，之后，脚本会重启
    # 再次运行时，脚本顶端的代码发现已经设定了环境变量，于是立即启动覆盖检测。
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    # 执行测试
    import unittest
    tests = unittest.TestLoader().discover('tests/unit')
    unittest.TextTestRunner(verbosity=2).run(tests)
    # 输出覆盖报告
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == '__main__':
    manager.run()
