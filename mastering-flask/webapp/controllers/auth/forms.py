# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
# from flask_wtf import RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Regexp, \
    ValidationError
from ...models import User


class LoginForm(FlaskForm):
    username_or_email = StringField(
        'Username or Email',
        validators=[DataRequired(), Length(max=255)])
    password = PasswordField(
        'Password',
        validators=[DataRequired()])
    remember = BooleanField('Remember me')

    def validate(self):
        check_validate = super(LoginForm, self).validate()
        if not check_validate:
            return False

        # check the user exist or not, then check the email exists or not
        user = User.query.filter_by(
            username=self.username_or_email.data).first()
        if not user:
            user = User.query.filter_by(
                email=self.username_or_email.data).first()
            if not user:
                self.username_or_email.errors.append(
                    'Invalid username or password')
                return False

        # check the password match or not
        if not user.check_password(self.password.data):
            self.username_or_email.errors.append('Invalid username or password')
            return False

        return True


class RegisterForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(max=255),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Usernames must have only letters, '
                   'numbers, dots or underscores')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=3)])
    confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            # EqualTo参数：需要确认的字段的变量名，以字符串的形式提供
            EqualTo('password', message='Passwords must match.')
        ]
    )
    # recaptcha = RecaptchaField()

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ChangepasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Submit Request')


class PasswordResetForm(FlaskForm):
    new_password = PasswordField(
        'New password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(FlaskForm):
    email = StringField(
        'New Email',
        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Change Email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
