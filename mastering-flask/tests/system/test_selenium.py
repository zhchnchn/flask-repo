# -*- coding: utf-8 -*-
import re
import threading
import time
import unittest
from selenium import webdriver
from webapp import create_app
from webapp.models import db, User, Role, Post, Tag, Comment
from webapp.extensions import admin, rest_api


# @unittest.skip('cannot pass')
class SeleniumTestCase(unittest.TestCase):
    def setUp(self):
        # start Firefox
        try:
            self.client = webdriver.Firefox()
        except:
            pass

        # skip these tests if the browser could not be started
        if self.client:
            # 设置浏览器窗口大小
            # cls.client.set_window_size(620, 600)  # 报错
            self.client.maximize_window()

            # Bug workarounds: Flask Admin和Flask Restful扩展中，
            # 它们会为应用生成蓝图对象并在内部保存起来，但在应用销毁时不会主动将其移除。
            admin._views = []
            rest_api.resources = []
            # create the application
            self.app = create_app('test')
            # 必须push context，否则会报错误
            self.app_context = self.app.app_context()
            self.app_context.push()

            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # Bug workaround: 如果不在webapp目录中运行，
            # 则Flask SQLAlchemy的初始化代码就不能正确地在应用对象中进行初始化
            db.app = self.app
            # create the database and populate with some fake data
            db.create_all()

            Role.generate_fake()
            User.generate_fake(10)
            Tag.generate_fake()
            Post.generate_fake(10)

            # start the Flask server in a thread
            threading.Thread(target=self.app.run).start()

            # give the server some time to ensure it is up
            time.sleep(3)

    def tearDown(self):
        if self.client:
            # stop the flask server and the browser
            self.client.get('http://localhost:5000/shutdown')
            self.client.close()

            # destroy database
            db.session.remove()
            db.drop_all()
            # remove application context
            self.app_context.pop()

    def test_admin_home_page(self):
        # navigate to home page
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Guest', self.client.page_source))

        # navigate to login page
        self.client.find_element_by_link_text('Log In').click()
        self.assertTrue('Login' in self.client.page_source)

        # login
        self.client.find_element_by_name('username_or_email'). \
            send_keys('admin@163.com')
        self.client.find_element_by_name('password').send_keys('admin')
        self.client.find_element_by_name('submit').click()
        time.sleep(1)
        self.assertTrue(re.search('Hello,\s+admin', self.client.page_source))

    def test_add_new_post(self):
        """
        测试是否可使用文章创建页面新增一篇文章
        1. 用户登录网站
        2. 前往新文章创建页面
        3. 填写表单各域，并提交表单
        4. 前往博客首页，确认这篇新文章出现在首页
        """

        # 登录
        self.client.get("http://localhost:5000/auth/login")

        username_field = self.client.find_element_by_name("username_or_email")
        username_field.send_keys("user01")

        password_field = self.client.find_element_by_name("password")
        password_field.send_keys("user01")

        # login_button = self.driver.find_element_by_id("login_button")
        login_button = self.client.find_element_by_xpath(".//*[@value='Login']")
        login_button.click()

        # 填写表单
        self.client.get("http://localhost:5000/blog/new")
        self.client.implicitly_wait(10)

        title_field = self.client.find_element_by_name("title")
        title_field.send_keys("Test Title")

        # 定位到 iframe 里面的编辑器
        self.client.switch_to.frame(
            self.client.find_element_by_tag_name("iframe")
        )
        post_field = self.client.find_element_by_class_name("cke_editable")
        post_field.send_keys("Test content")
        self.client.switch_to.parent_frame()

        post_button = self.client.find_element_by_class_name("btn-primary")
        post_button.click()

        # 确认文章已经创建
        self.client.get("http://localhost:5000/blog/")
        self.assertIn("Test Title", self.client.page_source)
        self.assertIn("Test content", self.client.page_source)


if __name__ == '__main__':
    unittest.main()

