# -*- coding: utf-8 -*-
from flask import redirect, url_for
from . import main_blueprint


@main_blueprint.route('/')
def index():
    return redirect(url_for('blog.home'))
