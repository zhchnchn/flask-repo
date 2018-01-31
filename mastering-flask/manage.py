# -*- coding: utf-8 -*-
import os
from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from flask_migrate import Migrate, MigrateCommand, upgrade
from webapp import create_app
from webapp.models import db, User, Post, Tag, Comment, Role, Follow

# 保证在全局作用域中的所有代码执行之前，启动覆盖检测
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='webapp/*')
    COV.start()


# 导入environment.txt中设置的环境变量
if os.path.exists('environment.txt'):
    print('Importing environment from environment.txt...')
    for line in open('environment.txt'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


# 读取环境变量FLASK_CONFIG, 若没设置则默认使用 default 配置
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
    tests = unittest.TestLoader().discover('tests')
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


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    # clear the sqlite data
    clear_data()
    print('completed clear data')
    # migrate database to latest revision
    upgrade()
    print('completed upgrade')
    # insert data
    insert_data()
    print('completed insert data')
    # unit test
    test(coverage=True)
    print('completed test')


if __name__ == '__main__':
    manager.run()
