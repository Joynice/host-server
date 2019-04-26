# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from ..forms import BaseForm
from wtforms import StringField, IntegerField
from wtforms.validators import Email, InputRequired, Length, Regexp, ValidationError
from utils import zlcache


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