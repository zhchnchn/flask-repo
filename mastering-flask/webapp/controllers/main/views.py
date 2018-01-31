# -*- coding: utf-8 -*-
from flask import redirect, url_for, current_app, abort, request
from . import main_blueprint


@main_blueprint.route('/')
def index():
    return redirect(url_for('blog.home'))


@main_blueprint.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
