# -*- coding: utf-8 -*-
import unittest
from webapp.models import User


class UserModelTestCase(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
