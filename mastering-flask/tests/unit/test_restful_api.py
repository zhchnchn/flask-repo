# -*- coding: utf-8 -*-
import unittest
import json
from base64 import b64encode
from flask import url_for
from webapp import create_app
from webapp.models import db, User, Role, Post, Comment
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
        self.client = self.app.test_client()

        # Bug workaround: 如果不在webapp目录中运行，
        # 则Flask SQLAlchemy的初始化代码就不能正确地在应用对象中进行初始化
        db.app = self.app
        db.create_all()

        # create role
        poster = Role(name='poster')
        db.session.add(poster)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 辅助方法，返回所有请求都要发送的通用首部，其中包含认证密令和MIME类型相关的首部。
    # 大多数测试都要发送这些首部。
    def get_api_headers(self, username_or_token, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username_or_token + ':' + password).encode('utf-8')
            ).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['error'] == '404 - page not found')

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_posts'),
                                   content_type='application/json')
        self.assertTrue(response.status_code == 200)

    def test_bad_auth(self):
        # add a user
        r = Role.query.filter_by(name='poster').first()
        self.assertIsNotNone(r)
        u = User('john')
        u.email = 'john@example.com'
        u.password = 'cat'
        u.confirmed = True
        u.roles.append(r)
        db.session.add(u)
        db.session.commit()

        # authenticate with bad password
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('john', 'dog'))
        self.assertTrue(response.status_code == 401)

    def test_token_auth(self):
        # add a user
        r = Role.query.filter_by(name='poster').first()
        self.assertIsNotNone(r)
        u = User('john')
        u.email = 'john@example.com'
        u.password = 'cat'
        u.confirmed = True
        u.roles.append(r)
        db.session.add(u)
        db.session.commit()

        # issue a request with a bad token
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)

        # get a token
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('john', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)

    def test_anonymous(self):
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('', ''))
        self.assertTrue(response.status_code == 200)

    def test_unconfirmed_account(self):
        # add an unconfirmed user
        r = Role.query.filter_by(name='poster').first()
        self.assertIsNotNone(r)
        u = User('john')
        u.email = 'john@example.com'
        u.password = 'cat'
        u.confirmed = False
        u.roles.append(r)
        db.session.add(u)
        db.session.commit()

        # get list of posts with the unconfirmed account
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('john', 'cat'))
        self.assertTrue(response.status_code == 403)

    def test_posts(self):
        # add a user
        r = Role.query.filter_by(name='poster').first()
        self.assertIsNotNone(r)
        u = User('john')
        u.email = 'john@example.com'
        u.password = 'cat'
        u.confirmed = True
        u.roles.append(r)
        db.session.add(u)
        db.session.commit()

        # write an empty post, will raise ValidationError
        response = self.client.post(
            url_for('api.new_post'),
            headers=self.get_api_headers('john', 'cat'),
            data=json.dumps({'text': ''}))
        self.assertTrue(response.status_code == 400)

        # write a post
        response = self.client.post(
            url_for('api.new_post'),
            headers=self.get_api_headers('john', 'cat'),
            data=json.dumps({
                'title': 'title of the post',
                'text': 'body of the *blog* post'
            })
        )
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # get the new post
        response = self.client.get(
            url,
            headers=self.get_api_headers('john', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['title'] == 'title of the post')
        self.assertTrue(json_response['text'] == 'body of the *blog* post')
        json_post = json_response

        # get the post from the user
        response = self.client.get(
            url_for('api.get_user_posts', id=u.id),
            headers=self.get_api_headers('john', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertTrue(json_response.get('count', 0) == 1)
        self.assertTrue(json_response['posts'][0] == json_post)

        # get the post from the user as a follower
        # 没有实现自关注，因此这里得不到
        response = self.client.get(
            url_for('api.get_user_following_posts', id=u.id),
            headers=self.get_api_headers('john', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertListEqual(json_response.get('posts'), [])
        self.assertTrue(json_response.get('count', -1) == 0)

        # edit post
        response = self.client.put(
            url,
            headers=self.get_api_headers('john', 'cat'),
            data=json.dumps({
                'title': 'updated title',
                'text': 'updated body'
            })
        )
        # self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['text'] == 'updated body')
        self.assertTrue(json_response['title'] == 'updated title')

    def test_users(self):
        # add two users
        r = Role.query.filter_by(name='poster').first()
        self.assertIsNotNone(r)
        u1 = User('john')
        u1.email = 'john@example.com'
        u1.password = 'cat'
        u1.confirmed = True
        u1.roles.append(r)
        u2 = User('susan')
        u2.email = 'susan@example.com'
        u2.password = 'dog'
        u2.confirmed = True
        u2.roles.append(r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # get users
        # 以u2通过验证，得到u1的用户信息
        response = self.client.get(
            url_for('api.get_user', id=u1.id),
            headers=self.get_api_headers('susan', 'dog'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['username'] == 'john')
        # 以u2通过验证，得到u2的用户信息
        response = self.client.get(
            url_for('api.get_user', id=u2.id),
            headers=self.get_api_headers('susan', 'dog'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['username'] == 'susan')

    def test_comments(self):
        # add two users
        r = Role.query.filter_by(name='poster').first()
        self.assertIsNotNone(r)
        u1 = User('john')
        u1.email = 'john@example.com'
        u1.password = 'cat'
        u1.confirmed = True
        u1.roles.append(r)
        u2 = User('susan')
        u2.email = 'susan@example.com'
        u2.password = 'dog'
        u2.confirmed = True
        u2.roles.append(r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # add a post
        post = Post(title='title of the post')
        post.text = 'body of the post'
        post.user = u1
        db.session.add(post)
        db.session.commit()

        # write a comment
        response = self.client.post(
            url_for('api.new_post_comment', id=post.id),
            headers=self.get_api_headers('susan', 'dog'),
            data=json.dumps({
                'name': 'comment name',
                'text': 'Good [post](http://example.com)!'
            })
        )
        self.assertTrue(response.status_code == 201)
        json_response = json.loads(response.data.decode('utf-8'))
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
        self.assertTrue(json_response['name'] == 'comment name')
        self.assertTrue(json_response['text'] ==
                        'Good [post](http://example.com)!')

        # get the new comment
        response = self.client.get(
            url,
            headers=self.get_api_headers('john', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['name'] == 'comment name')
        self.assertTrue(json_response['text'] ==
                        'Good [post](http://example.com)!')

        # add another comment
        comment = Comment(name='another comment name')
        comment.text = 'Thank you!'
        comment.user = u1
        comment.post = post
        db.session.add(comment)
        db.session.commit()

        # get the two comments from the post
        response = self.client.get(
            url_for('api.get_post_comments', id=post.id),
            headers=self.get_api_headers('susan', 'dog'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertTrue(json_response.get('count', 0) == 2)

        # get all the comments
        response = self.client.get(
            url_for('api.get_comments', id=post.id),
            headers=self.get_api_headers('susan', 'dog'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertTrue(json_response.get('count', 0) == 2)


if __name__ == '__main__':
    unittest.main()

