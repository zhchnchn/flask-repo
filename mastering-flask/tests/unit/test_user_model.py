# -*- coding: utf-8 -*-
import unittest
import time
import datetime
from webapp import create_app
from webapp.models import db, User, Follow
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
        # 只有commit了才能拿到id，以便生成token
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

    def test_valid_reset_token(self):
        user = User('test')
        user.password = 'cat'
        user.email = 'test@163.com'
        db.session.add(user)
        # 只有commit了才能拿到id，以便生成token
        db.session.commit()
        token = user.generate_reset_token(user.email)
        self.assertTrue(user.reset_password(token, 'dog'))
        self.assertTrue(user.check_password('dog'))

    def test_invalid_reset_token(self):
        user1 = User('test1')
        user2 = User('test2')
        user1.password = 'cat'
        user2.password = 'dog'
        user1.email = 'test1@163.com'
        user2.email = 'test2@163.com'
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        token = user1.generate_reset_token(user1.email)
        self.assertFalse(user2.reset_password(token, 'puppy'))
        self.assertTrue(user2.check_password('dog'))

    def test_valid_email_change_token(self):
        user1 = User('test1')
        user1.email = 'test1@163.com'
        user1.password = 'cat'
        db.session.add(user1)
        db.session.commit()
        token = user1.generate_email_change_token('test1@example.com')
        self.assertTrue(user1.change_email(token))
        self.assertTrue(user1.email == 'test1@example.com')

    def test_invalid_email_change_token(self):
        user1 = User('test1')
        user1.email = 'test1@163.com'
        user1.password = 'cat'
        user2 = User('test2')
        user2.email = 'test2@163.com'
        user2.password = 'dog'
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        token = user1.generate_email_change_token('test1@example.com')
        self.assertFalse(user2.change_email(token))
        self.assertTrue(user2.email == 'test2@163.com')

    def test_duplicate_email_change_token(self):
        user1 = User('test1')
        user1.email = 'test1@163.com'
        user1.password = 'cat'
        user2 = User('test2')
        user2.email = 'test2@163.com'
        user2.password = 'dog'
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        token = user2.generate_email_change_token('test1@163.com')
        self.assertFalse(user2.change_email(token))
        self.assertTrue(user2.email == 'test2@163.com')

    def test_follows(self):
        u1 = User('test1')
        u1.email = 'test1@163.com'
        u1.password = 'cat'
        u2 = User('test2')
        u2.email = 'test2@163.com'
        u2.password = 'dog'
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))

        timestamp_before = datetime.datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.following.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        f = u1.following.all()[-1]
        self.assertTrue(f.following == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)

        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.following.count() == 0)
        self.assertTrue(u2.followers.count() == 0)
        self.assertTrue(Follow.query.count() == 0)

        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 0)


if __name__ == '__main__':
    unittest.main()
