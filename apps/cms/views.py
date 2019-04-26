# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from flask import Blueprint, views, render_template, request, session, redirect, url_for, g
from .forms import LoginForm
from .models import User
from config import config
from .decorators import login_required, permission_required
from api import field
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

bp.add_url_rule('login/', view_func=LoginView.as_view('login'))