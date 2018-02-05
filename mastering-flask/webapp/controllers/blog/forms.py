# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    text = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Add Comment')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    text = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ProfileEditForm(FlaskForm):
    # 这个表单中的所有字段都是可选的，因此长度验证函数允许长度为零
    name = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 255)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Update Profile')
