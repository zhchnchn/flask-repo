# -*- coding: utf-8 -*-
import os
from flask import Blueprint


blog_blueprint = Blueprint('blog', __name__,
                           # template_folder='../../templates/blog'
                           template_folder=os.path.join(
                               os.path.pardir, os.path.pardir,
                               'templates', 'blog'),
                           url_prefix='/blog')

from . import views