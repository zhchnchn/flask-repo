# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, request, url_for, flash, render_template
from flask_login import login_user, logout_user
from ..forms import LoginForm, RegisterForm
from ..models import db, User


auth_blueprint = Blueprint('auth', __name__,
                           template_folder='../templates/auth',
                           url_prefix='/auth')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)

        flash("You have been logged in.", category="success")
        # 重定向到前一次要访问的页面，没有的话重定向到首页
        print(request.args.get('next'))
        return redirect(request.args.get('next') or url_for('blog.home'))

    return render_template('login.html', form=form)


@auth_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()

    flash("You have been logged out.", category="success")
    return redirect(url_for('.login'))


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(form.username.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash("Your user has been created, please login.", category="success")
        return redirect(url_for('.login'))

    return render_template('register.html', form=form)
