# -*- coding: utf-8 -*-
import unittest
import re

from flask import url_for
from webapp import create_app
from webapp.models import db, User, Role
from webapp.extensions import admin, rest_api


class UrlsTestCase(unittest.TestCase):

    def setUp(self):
        # Bug workarounds: Flask Admin和Flask Restful扩展中，
        # 它们会为应用生成蓝图对象并在内部保存起来，但在应用销毁时不会主动将其移除。
        admin._views = []
        rest_api.resources = []

        self.app = create_app('test')
        # 必须push context，否则会报错误
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

        # Bug workaround: 如果不在webapp目录中运行，
        # 则Flask SQLAlchemy的初始化代码就不能正确地在应用对象中进行初始化
        db.app = self.app
        db.create_all()

        # create role and user
        # 由于下面有个test_register_and_login测试，要注册新用户，
        # 在register路由中会默认添加上'poster'和'default'角色，因此这里要先创建两种角色
        poster = Role('poster')
        poster.description = 'poster role'
        default = Role('default')
        default.description = 'default role'
        db.session.add(poster)
        db.session.add(default)

        test_user = User('test')
        test_user.email = 'test@163.com'
        test_user.password = 'test'
        test_user.confirmed = True
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

    def test_home_page(self):
        response = self.client.get(url_for('blog.home'))
        self.assertTrue('Guest' in response.data)

    def test_login_with_username(self):
        """ Tests if the login with username works correctly """
        result = self.client.post(
            '/auth/login',
            data=dict(username_or_email='test', password='test'),
            follow_redirects=True  # 追踪跳转
        )
        self.assertIn("You have been logged in.", result.data)

    def test_login_with_email(self):
        """ Tests if the login with email works correctly """
        result = self.client.post(
            '/auth/login',
            data=dict(username_or_email='test@163.com', password='test'),
            follow_redirects=True  # 追踪跳转
        )
        self.assertIn("You have been logged in.", result.data)

    def test_logout(self):
        """ Tests if the logout form works correctly """
        result = self.client.post(
            '/auth/login',
            data=dict(username_or_email='test', password='test'),
            follow_redirects=True  # 追踪跳转
        )

        self.assertEqual(result.status_code, 200)
        self.assertIn("You have been logged in.", result.data)

        result = self.client.get(
            '/auth/logout',
            follow_redirects=True
        )

        self.assertEqual(result.status_code, 200)
        self.assertIn("You have been logged out.", result.data)

    def test_register_and_login(self):
        # 注册新账户
        # post()方法的data参数是个字典，包含表单中的各个字段，各字段的名字必须严格匹配定义表单时使用的名字。
        response = self.client.post(
            url_for('auth.register'),
            data={
                'email': 'john@example.com',
                'username': 'john',
                'password': 'cat',
                'confirm': 'cat'
            }
        )
        # 如果注册成功，会返回一个重定向，把用户转到登录页面。
        self.assertTrue(response.status_code == 302)

        # 使用新注册的账户登录
        response = self.client.post(
            url_for('auth.login'),
            data={
                'username_or_email': 'john@example.com',
                'password': 'cat'
            },
            follow_redirects=True
        )
        self.assertTrue(re.search('Hello,\s+john!', response.data))
        self.assertTrue(
            'You have not confirmed your account yet' in response.data)

        # 发送确认令牌
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(
            url_for('auth.confirm', token=token),
            follow_redirects=True
        )
        self.assertTrue(
            'You have confirmed your account' in response.data)

        # 退出
        response = self.client.get(
            url_for('auth.logout'),
            follow_redirects=True
        )
        self.assertTrue('You have been logged out' in response.data)


if __name__ == '__main__':
    unittest.main()

