# -*- coding: utf-8 -*-
from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__,
                           template_folder='../../templates/auth',
                           url_prefix='/auth')

# 这里导入views，纯粹是为了将views中的路由暴露出来，这样外部只导入该文件就可以了，
# 由于views中也导入了auth_blueprint，导致循环依赖，所以这里把导入views放在了文件最后
from . import views
