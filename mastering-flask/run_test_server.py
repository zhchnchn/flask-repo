# -*- coding: utf-8 -*-
"""
结合tests/test_ui.py使用
"""
from webapp import create_app
from webapp.models import db, User, Role

app = create_app('test')

# Bug workaround
db.app = app
db.create_all()


default = Role("default")
poster = Role("poster")
db.session.add(default)
db.session.add(poster)

test_user = User("test")
test_user.password = 'test'
test_user.confirmed = True
test_user.email = 'test@163.com'
test_user.roles.append(poster)
db.session.add(test_user)
db.session.commit()

app.run()
