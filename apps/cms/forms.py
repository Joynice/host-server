# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from ..forms import BaseForm
from wtforms import StringField, IntegerField
from wtforms.validators import Email, InputRequired, Length, Regexp, ValidationError, EqualTo
from utils import zlcache
from flask import g

class LoginForm(BaseForm):
    email = StringField(validators=[Email(message='请输入正确的邮箱格式'), InputRequired(message='请输入邮箱')])
    password = StringField(validators=[Length(6, 20, message='请输入正确格式的密码'), InputRequired(message='请输入密码')])
    graph_captcha = StringField(validators=[Regexp(r'\w{4}', message='请输入正确格式的图形验证码！'), InputRequired(message='请输入验证码')])
    remember = IntegerField()

    def validate_graph_captcha(self, field):
        graph_captcha = field.data
        print(graph_captcha,11111111111111111111)
        graph_captcha_mem = zlcache.get(graph_captcha.lower())
        if not graph_captcha_mem:
            raise ValidationError(message='图形验证码错误！')


class ResetEmailForm(BaseForm):
    email = StringField(validators=[Email(message='请输入正确的邮箱格式'), InputRequired(message='请输入邮箱')])
    captcha = StringField(validators=[Length(min=6, max=6, message='请输入正确格式的验证码'), InputRequired(message='请输入验证码')])

    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_cache = zlcache.get(email)
        if not captcha_cache or captcha.lower() !=captcha_cache.lower():
            raise ValidationError('邮箱验证码错误')

    def validate_email(self, field):
        email = field.data
        user = g.cms_user
        if user.email == email:
            raise ValidationError('不能使用相同的邮箱进行修改')

class ResetpwdForm(BaseForm):
    oldpwd = StringField(validators=[Length(6, 20, message='请输入正确格式的旧密码'), InputRequired(message='请输入旧密码')])
    newpwd = StringField(validators=[Length(6, 20, message='请输入正确格式的新密码'), InputRequired(message='请输入新密码')])
    newpwd2 = StringField(validators=[EqualTo('newpwd', message='确认密码必须和新密码保持一致'), InputRequired(message='请再次输入新密码')])