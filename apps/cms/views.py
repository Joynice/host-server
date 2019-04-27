# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from flask import Blueprint, views, render_template, request, session, redirect, url_for, g
from .forms import LoginForm, ResetEmailForm, ResetpwdForm
from .models import User
from config import config
from .decorators import login_required, permission_required
from api import field
from exts import db
import string
import random
from utils import zlcache
bp = Blueprint('admin', __name__, url_prefix='/')

#首页
@bp.route('admin/')
@login_required
def index():
    return render_template('cms/cms_index.html')

#注销
@bp.route('logout/')
@login_required
def logout():
    del session[config['development'].CMS_USER_ID]
    return redirect(url_for('admin.login'))

#个人信息
@bp.route('profile/')
@login_required
def profile():
    return render_template('cms/cms_profile.html')

#发送邮件
@bp.route('email_captcha/')
@login_required
def email_captcha():
    from tasks import send_mail
    email = request.args.get('email')
    print(email)
    if not email:
        return field.params_error('请传递邮箱参数！')
    source = list(string.ascii_letters)
    source.extend(map(lambda x: str(x), range(0, 10)))
    captcha = "".join(random.sample(source, 6))
    # message = Message('BBS论坛邮箱验证码', recipients=[email], body='您的验证码是：{}'.format(captcha))
    send_mail.delay('牧羊人邮箱验证码', [email], '您的验证码是：{}'.format(captcha))
    # try:
    #     mail.send(message)
    # except Exception as e:
    #     return restful.server_error(message=e)
    zlcache.set(email, captcha)
    return field.success()

#登录
class LoginView(views.MethodView):
    def get(self, message=None):
        return render_template('cms/login.html', message=message)

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            print(email, password ,remember)
            user = User.query.filter_by(email=email).first()
            print(user)
            if user and user.check_password(password):
                session[config['development'].CMS_USER_ID] = user.id  # 保存用户登录信息
                if remember:
                    # 如果设置session.permanent = True，那么过期时间为31天
                    session.permanent = True
                return field.success(message='登陆成功！')
            else:
                return field.params_error(message='邮箱或者密码错误')

        else:
            print(form.errors)
            message = form.get_error()
            return field.params_error(message=message)


#重置邮箱
class ResetEmail(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('cms/cms_resetemail.html')

    def post(self):
        form = ResetEmailForm(request.form)
        if form.validate():
            email = form.email.data
            g.cms_user.email = email
            db.session.commit()

            return field.success()
        else:
            return field.params_error(form.get_error())

#重置密码
class ReetPWView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('cms/cms_resetpw.html')

    def post(self):
        form = ResetpwdForm(request.form)
        if form.validate():
            oldpwd = form.oldpwd.data
            newpwd = form.newpwd.data
            user = g.cms_user
            if user.check_password(oldpwd):
                user.password = newpwd
                db.session.commit()
                return field.success()
            else:
                return field.params_error('旧密码错误！')
        else:
            message = form.get_error()
            return field.unauth_error(message=message)


bp.add_url_rule('login/', view_func=LoginView.as_view('login'))
bp.add_url_rule('resetemail/', view_func=ResetEmail.as_view('resetemail'))
bp.add_url_rule('resetpw/', view_func=ReetPWView.as_view('resetpw'))