# -*- coding: utf-8 -*-
from flask import Blueprint


# 由于blog蓝图添加了URL前缀，因此在基础app对象上已经没有任何视图了，访问网站的根路径，
# 将没有对应的视图函数，因此添加一个main蓝图，该蓝图不设置URL前缀, 仅在根路径上加一个重定向
main_blueprint = Blueprint('main', __name__,
                           template_folder='../../templates/blog')

from . import views