# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
# from flask_wtf import RecaptchaField
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, \
    widgets
from wtforms.validators import DataRequired, Length, EqualTo
from models import User


# ******************* blog_blueprint forms *********************************** #

class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    text = TextAreaField('Comment', validators=[DataRequired()])


class PostForm(FlaskForm):
    title = StringField('Title', [DataRequired(), Length(max=255)])
    text = TextAreaField('Content', [DataRequired()])


# ******************* auth_blueprint forms *********************************** #

class LoginForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(max=255)])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember me')

    def validate(self):
        check_validate = super(LoginForm, self).validate()
        if not check_validate:
            return False

        # check the user exist or not
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Invalid username or password')
            return False

        # check the password match or not
        if not user.check_password(self.password.data):
            self.username.errors.append('Invalid username or password')
            return False

        return True


class RegisterForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(max=255)])
    password = PasswordField('Password', [DataRequired(), Length(min=3)])
    # EqualTo参数：需要确认的字段的变量名，以字符串的形式提供
    confirm = PasswordField('Confirm Password',
                            [DataRequired(), EqualTo('password')])
    # recaptcha = RecaptchaField()

    def validate(self):
        check_validate = super(RegisterForm, self).validate()

        if not check_validate:
            return False

        # check whether the username already being used or not
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append('User already exists with same name')
            return False

        return True


# ******************* Flask-Admin forms ************************************** #

class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()
