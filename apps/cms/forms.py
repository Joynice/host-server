# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from ..forms import BaseForm
from wtforms import StringField, IntegerField
from wtforms.validators import Email, InputRequired, Length, Regexp, ValidationError, EqualTo
from utils import zlcache
from flask import g
from .models import User

#登录验证
class LoginForm(BaseForm):
    email = StringField(validators=[Email(message='请输入正确的邮箱格式'), InputRequired(message='请输入邮箱')])
    password = StringField(validators=[Length(6, 20, message='请输入正确格式的密码'), InputRequired(message='请输入密码')])
    graph_captcha = StringField(validators=[Regexp(r'\w{4}', message='请输入正确格式的图形验证码！'), InputRequired(message='请输入验证码')])
    remember = IntegerField()

    def validate_graph_captcha(self, field):
        graph_captcha = field.data
        graph_captcha_mem = zlcache.get(graph_captcha.lower())
        if not graph_captcha_mem:
            raise ValidationError(message='图形验证码错误！')

#重置邮箱验证
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

#重置密码验证
class ResetpwdForm(BaseForm):
    oldpwd = StringField(validators=[Length(6, 20, message='请输入正确格式的旧密码'), InputRequired(message='请输入旧密码')])
    newpwd = StringField(validators=[Length(6, 20, message='请输入正确格式的新密码'), InputRequired(message='请输入新密码')])
    newpwd2 = StringField(validators=[EqualTo('newpwd', message='确认密码必须和新密码保持一致'), InputRequired(message='请再次输入新密码')])


#添加任务
class AddTaskFoem(BaseForm):
    url1 = StringField(validators=[InputRequired(message='请输入任务URL！')])
    cycle = IntegerField()
    number = IntegerField(validators=[InputRequired(message='请输入扫描次数！')])

#更新任务
class UpgradeTaskForm(BaseForm):
    task_id = IntegerField(validators=[InputRequired(message='未传入任务ID')])
    url1 = StringField(validators=[InputRequired(message='请输入任务URL！')])
    cycle = IntegerField()
    number = IntegerField(validators=[InputRequired(message='请输入扫描次数！')])

#删除任务
class DeleteTaskForm(BaseForm):
    task_id = IntegerField(validators=[InputRequired(message='未传入任务ID')])

#增加cms指纹
class AddCmsForm(BaseForm):
    url = StringField()
    name = StringField(validators=[InputRequired(message='请输入CMS名称')])
    re = StringField()
    md5 = StringField()

#更新cms指纹
class UpgradeCmsForm(BaseForm):
    cms_id = IntegerField(validators=[InputRequired(message='未传入ID')])
    url = StringField()
    name = StringField(validators=[InputRequired(message='请输入CMS名称')])
    re = StringField()
    md5 = StringField()

#删除mcs指纹
class DeleteCmsForm(BaseForm):
    cms_id = IntegerField(validators=[InputRequired(message='未传入ID')])

#添加用户
class AddUserForm(BaseForm):
    username = StringField(validators=[Regexp(r'.{2,20}', message='请输入正确格式的用户名！'), InputRequired(message='请输入用户名！')])
    password = StringField(validators=[Regexp(r'[0-9a-zA-Z_\./]{6,20}', message='密码必须6-20位数字或字母之间'), InputRequired(message='请输入密码！')])
    email_capt = StringField(validators=[Length(min=6, max=6, message='请输入正确格式的邮箱验证码'), InputRequired('请输入邮箱验证码')])
    email = StringField(validators=[InputRequired(message='请输入邮箱地址！')])
    role = StringField(validators=[InputRequired(message='请选择角色!')])

    def validate_username(self, field):
        username = field.data
        user = User.query.filter_by(username=username).first()
        if user:
            raise ValidationError('该昵称已经被使用！')

    def validate_email_capt(self, field):
        captcha = field.data
        email = self.email.data
        captcha_cache = zlcache.get(email)
        if not captcha_cache or captcha.lower() !=captcha_cache.lower():
            raise ValidationError('邮箱验证码错误')
#修改用户信息
class UpdateUserForm(BaseForm):
    user_id = StringField(validators=[InputRequired(message='没有改用户信息')])
    username = StringField(validators=[Regexp(r'.{2,20}', message='请输入正确格式的用户名！'), InputRequired(message='请输入用户名！')])
    email = StringField(validators=[InputRequired(message='请输入邮箱地址！')])
    role = StringField(validators=[InputRequired(message='请选择角色!')])
    email_capt = StringField()

    def validate_email_capt(self, field):

        captcha = field.data
        if captcha:
            email = self.email.data
            captcha_cache = zlcache.get(email)
            if not captcha_cache or captcha.lower() !=captcha_cache.lower():
                raise ValidationError('邮箱验证码错误')
        else:
            pass

#管理员更改任务
class UpgradeAdminTaskForm(BaseForm):
    task_id = IntegerField(validators=[InputRequired(message='未传入任务ID')])
    url1 = StringField(validators=[InputRequired(message='请输入任务URL！')])
    cycle = IntegerField()
    number = IntegerField(validators=[InputRequired(message='请输入扫描次数！')])

#管理员删除任务
class DeleteAdminTaskForm(BaseForm):
    task_id = IntegerField(validators=[InputRequired(message='未传入任务ID')])

