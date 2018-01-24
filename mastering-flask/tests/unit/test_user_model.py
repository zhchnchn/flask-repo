# -*- coding: utf-8 -*-
import unittest
import time
from webapp import create_app
from webapp.models import db, User
from webapp.extensions import admin, rest_api


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        # Bug workarounds: Flask Admin和Flask Restful扩展中，
        # 它们会为应用生成蓝图对象并在内部保存起来，但在应用销毁时不会主动将其移除。
        admin._views = []
        rest_api.resources = []

        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Bug workaround: 如果不在webapp目录中运行，
        # 则Flask SQLAlchemy的初始化代码就不能正确地在应用对象中进行初始化
        db.app = self.app
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        user = User('test')
        user.password = 'cat'
        self.assertTrue(user.password_hash is not None)

    def test_no_password_getter(self):
        user = User('test')
        user.password = 'cat'
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User('test')
        user.password = 'cat'
        self.assertTrue(user.check_password('cat'))
        self.assertFalse(user.check_password('dog'))

    def test_password_salts_are_random(self):
        user01 = User('test01')
        user01.password = 'cat'
        user02 = User('test02')
        user02.password = 'cat'
        self.assertTrue(user01.password_hash != user02.password_hash)

    def test_valid_confirmation_token(self):
        user = User('test')
        user.password = 'cat'
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        self.assertTrue(user.confirm(token))

    def test_invalid_confirmation_token(self):
        user1 = User('test1')
        user2 = User('test2')
        user1.password = 'cat'
        user2.password = 'dog'
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        token = user1.generate_confirmation_token()
        self.assertFalse(user2.confirm(token))

    def test_expired_confirmation_token(self):
        user = User('test')
        user.password = 'cat'
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(user.confirm(token))


if __name__ == '__main__':
    unittest.main()
