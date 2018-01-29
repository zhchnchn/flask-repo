# -*- coding: utf-8 -*-
import os
from flask import Blueprint


blog_blueprint = Blueprint('blog', __name__,
                           # template_folder='../../templates/blog'
                           template_folder=os.path.join(
                               os.path.pardir, os.path.pardir,
                               'templates', 'blog'),
                           url_prefix='/blog')

# 这里导入views，纯粹是为了将views中的路由暴露出来，这样外部只导入该文件就可以了，
# 导入errors的原因同理
from . import views, errors
