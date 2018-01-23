# -*- coding: utf-8 -*-
import unittest
from selenium import webdriver


class UiTestCase(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.close()

    def test_add_new_post(self):
        """ 测试是否可使用文章创建页面新增一篇文章

           1. 用户登录网站
           2. 前往新文章创建页面
           3. 填写表单各域，并提交表单
           4. 前往博客首页，确认这篇新文章出现在首页
        """

        # 登录
        self.driver.get("http://localhost:5000/auth/login")

        username_field = self.driver.find_element_by_name("username")
        username_field.send_keys("test")

        password_field = self.driver.find_element_by_name("password")
        password_field.send_keys("test")

        # login_button = self.driver.find_element_by_id("login_button")
        login_button = self.driver.find_element_by_xpath(".//*[@value='Login']")
        login_button.click()

        # 填写表单
        self.driver.get("http://localhost:5000/blog/new")
        self.driver.implicitly_wait(10)

        title_field = self.driver.find_element_by_name("title")
        title_field.send_keys("Test Title")

        # 定位到 iframe 里面的编辑器
        self.driver.switch_to.frame(
            self.driver.find_element_by_tag_name("iframe")
        )
        post_field = self.driver.find_element_by_class_name("cke_editable")
        post_field.send_keys("Test content")
        self.driver.switch_to.parent_frame()

        post_button = self.driver.find_element_by_class_name("btn-primary")
        post_button.click()

        # 确认文章已经创建
        self.driver.get("http://localhost:5000/blog/")
        self.assertIn("Test Title", self.driver.page_source)
        self.assertIn("Test content", self.driver.page_source)


if __name__ == '__main__':
    unittest.main()

