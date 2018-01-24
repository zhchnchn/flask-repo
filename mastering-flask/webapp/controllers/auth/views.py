# -*- coding: utf-8 -*-
from flask import redirect, request, url_for, flash, \
    render_template, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from .forms import LoginForm, RegisterForm
from ...models import db, User
from ...email import send_email
from . import auth_blueprint


# 如果：
# 1. 用户已登录
# 2. 用户的账户还未确认
# 3. 请求的端点（使用request.endpoint获取）不是认证URL中，且不是访问static文件的URL。
# 则会被重定向到/auth/unconfirmed路由，要求用户先确认账户。
@auth_blueprint.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('.unconfirmed'))


@auth_blueprint.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('blog.home'))
    return render_template('unconfirmed.html')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username_or_email.data).first()
        if user is not None:
            # login_user()函数的参数是要登录的用户，以及可选的“记住我”布尔值
            login_user(user, form.remember.data)
        else:
            user = User.query.filter_by(
                email=form.username_or_email.data).first()
            # 不需要判断，LoginForm的validate函数会做检验，上面对username之所以判断
            # 是由于如果username不存在，还要检测email是否存在
            # if user is not None:
            login_user(user, form.remember.data)

        # identity changed
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(user.id))

        flash("You have been logged in.", category="success")
        # 重定向到前一次要访问的页面，没有的话重定向到首页
        return redirect(request.args.get('next') or url_for('blog.home'))

    return render_template('login.html', form=form)


@auth_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()

    # identity changed
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    flash("You have been logged out.", category="success")
    return redirect(url_for('.login'))


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(form.username.data)
        new_user.email = form.email.data
        new_user.password = form.password.data

        db.session.add(new_user)
        db.session.commit()

        # send confirmation email
        token = new_user.generate_confirmation_token()
        send_email(new_user.email, 'Confirm Your Account', 'auth/email/confirm',
                   user=new_user, token=token)
        flash('A confirmation email has been sent to you by email.', category="success")
        return redirect(url_for('.login'))

    return render_template('register.html', form=form)


# 这个路由用login_required保护，
# 用户点击确认邮件中的链接后，要先登录，然后才能执行这个视图函数
@auth_blueprint.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('blog.home'))

    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')

    return redirect(url_for('blog.home'))


# 这个路由也用login_required保护，确保访问时程序知道请求再次发送邮件的是哪个用户。
@auth_blueprint.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm',
               user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('blog.home'))
