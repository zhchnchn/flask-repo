# -*- coding: utf-8 -*-
from flask import redirect, request, url_for, flash, \
    render_template, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed, \
    IdentityContext
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .forms import LoginForm, RegisterForm, ChangepasswordForm, \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from ...models import db, User, Role
from ...email import send_email
from ...extensions import admin_permission
from . import auth_blueprint


# 上下文处理, 可以在Jinja2模板中判断是否有admin执行权限
# 参考：http://blog.csdn.net/qq850482461/article/details/76111609
@auth_blueprint.app_context_processor
def context():
    admin_context = IdentityContext(admin_permission)
    return dict(admin=admin_context)


# 如果：
# 1. 用户已登录
# 2. 用户的账户还未确认
# 3. 请求的端点（使用request.endpoint获取）不是认证URL中，且不是访问static文件的URL。
# 则会被重定向到/auth/unconfirmed路由，要求用户先确认账户。
@auth_blueprint.before_app_request
def before_request():
    if current_user.is_authenticated:
        # before_app_request处理程序会在每次请求前运行，所以在这里实现刷新last_seen字段的需求
        current_user.update_last_seen()

        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


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
        new_user = User(username=form.username.data)
        new_user.email = form.email.data
        new_user.password = form.password.data
        # 新注册用户默认具有poster及以下级别权限
        new_user.roles.append(Role.query.filter_by(name='poster').first())
        new_user.roles.append(Role.query.filter_by(name='default').first())

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
        flash('You have confirmed your account. Thanks!', category="success")
    else:
        flash('The confirmation link is invalid or has expired.', category="success")

    return redirect(url_for('blog.home'))


# 这个路由也用login_required保护，确保访问时程序知道请求再次发送邮件的是哪个用户。
@auth_blueprint.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm',
               user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.', category="success")
    return redirect(url_for('blog.home'))


@auth_blueprint.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangepasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', category='success')
            return redirect(url_for('blog.home'))
        else:
            flash('Your password is not correct.', category='warning')

    return render_template('change_password.html', form=form)


@auth_blueprint.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    # if the user is login, need not to reset password
    if not current_user.is_anonymous:
        return redirect('blog.home')

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token(form.email.data)
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password', user=user, token=token)
            flash('An email with instructions to reset your password has been '
                  'sent to you.', category='success')
        else:
            flash('The email is not registered yet.', category='warning')
        return redirect(url_for('blog.home'))

    return render_template('password_reset_request.html', form=form)


@auth_blueprint.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    # if the user is login, need not to reset password
    if not current_user.is_anonymous:
        return redirect('blog.home')

    form = PasswordResetForm()
    if form.validate_on_submit():
        # 如果邮箱对应的用户不存在，则不能重置密码
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        email = data.get('email')
        if email is None:
            return False
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('Your email is invalid or the token expiration', category='warning')
            return redirect(url_for('blog.home'))

        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated. Please Login',
                  category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Can not update your password', category='warning')
            return redirect(url_for('blog.home'))

    return render_template('password_reset.html', token=token, form=form)


@auth_blueprint.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.', category='success')
            return redirect(url_for('blog.home'))
        else:
            flash('Invalid password.', category='warning')
    return render_template("change_email.html", form=form)


@auth_blueprint.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.', category='success')
    else:
        flash('Invalid request.', category='warning')
    return redirect(url_for('blog.home'))
