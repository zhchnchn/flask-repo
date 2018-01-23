# -*- coding: utf-8 -*-
import unittest
from webapp import create_app
from webapp.models import db, User, Role
from webapp.extensions import admin, rest_api

class TestUrls(unittest.TestCase):

    def setUp(self):
        # Bug workarounds: Flask Admin和Flask Restful扩展中，
        # 它们会为应用生成蓝图对象并在内部保存起来，但在应用销毁时不会主动将其移除。
        admin._views = []
        rest_api.resources = []

        self.app = create_app('test')
        # 必须push context，否则会报错误
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Bug workaround: 如果不在webapp目录中运行，
        # 则Flask SQLAlchemy的初始化代码就不能正确地在应用对象中进行初始化
        db.app = self.app
        db.create_all()

        # create role and user
        poster = Role('poster')
        db.session.add(poster)

        test_user = User('test')
        test_user.password = 'test'
        test_user.roles.append(poster)
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_root_redirect(self):
        """ Tests if the root URL gives a 302 """
        result = self.client.get('/')
        self.assertEqual(result.status_code, 302)
        self.assertIn("/blog/", result.headers['Location'])

    def test_login(self):
        """ Tests if the login form works correctly """
        result = self.client.post(
            '/auth/login',
            data=dict(username='test', password='test'),
            follow_redirects=False  # 不追踪跳转
        )

        self.assertEqual(result.status_code, 302)

    def test_logout(self):
        """ Tests if the logout form works correctly """
        result = self.client.post(
            '/auth/login',
            data=dict(username='test', password='test'),
            follow_redirects=True  # 追踪跳转
        )

        self.assertEqual(result.status_code, 200)

        result = self.client.get(
            '/auth/logout',
            follow_redirects=True
        )

        self.assertEqual(result.status_code, 200)
        self.assertIn("You have been logged out.", result.data)


if __name__ == '__main__':
    unittest.main()

