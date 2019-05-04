# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import datetime
import os
import random
import string
import uuid
from threading import Lock

from flask import Blueprint, views, render_template, request, session, redirect, url_for, g
from flask_paginate import Pagination, get_page_parameter

from api import field
from config import config
from exts import db, socketio
from models import Cms_fingerprint
from utils import zlcache, rediscache, avatar as user_avatar
from .decorators import login_required, permission_required
from .filter import StringToInt, IntToString, IntToStatus, StatusToString, NoneToString
from .forms import LoginForm, ResetEmailForm, ResetpwdForm, UpgradeTaskForm, AddTaskFoem, DeleteTaskForm, \
    UpgradeCmsForm, DeleteCmsForm, AddCmsForm, AddUserForm, UpdateUserForm
from .models import User, CMSPersmission, Task, CMSRole

thread = None
async_mode = None
thread_lock = Lock()
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
    user = g.cms_user
    user.is_activate = IntToStatus(0)
    db.session.add(user)
    db.session.commit()
    del session[config['development'].CMS_USER_ID]
    return redirect(url_for('admin.login'))

# 允许上传文件类型
def allowd_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in config['development'].ALLOWED_EXTENSIONS

#个人信息
class ProFileView(views.MethodView):
    decorators = [login_required]

    def get(self):
        ip = request.remote_addr
        return render_template('cms/cms_profile.html', user_ip=ip)

    # 修改头像
    def post(self):
        file = request.files['avatar_upload']
        base_path = './static/cms/img/user/'
        filename = str(g.cms_user.email) + '.' + file.filename.rsplit('.', 1)[1]
        if not allowd_file(file.filename):
            return field.params_error('上传的文件格式不合法，请选择图片格式文件上传！')
        file_path = os.path.join(base_path, filename)
        print(file_path)
        for i in config['development'].ALLOWED_EXTENSIONS:
            try:
                print(os.path.join(base_path,g.cms_user.email)+'.'+ i)
                os.remove(os.path.join(base_path,g.cms_user.email)+'.'+i)
            except:
                pass
        file.save(file_path)
        user = g.cms_user
        user.avatar_path = '/static/cms/img/user/' + filename
        db.session.add(user)
        db.session.commit()
        return field.success('修改头像成功！')


#发送邮件
@bp.route('email_captcha/')
@login_required
def email_captcha():
    from tasks import send_mail
    email = request.args.get('email')
    if not email:
        return field.params_error('请传递邮箱参数！')
    user = User.query.filter_by(email=email).first()
    if user:
        return field.params_error('该邮箱已经注册，请更换邮箱！')
    source = list(string.ascii_letters)
    source.extend(map(lambda x: str(x), range(0, 10)))
    captcha = "".join(random.sample(source, 6))
    print(captcha)
    send_mail.delay('牧羊人邮箱验证码', [email], '您的验证码是：{}'.format(captcha))
    zlcache.set(email, captcha)
    return field.success()


# 任务页面
@bp.route('task/')
@login_required
@permission_required(CMSPersmission.POST)
def task():
    tasks = g.cms_user.tasks
    context = {
        'tasks': tasks
    }
    return render_template('cms/cms_task.html', **context)


# 添加任务
@bp.route('atask/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.POST)
def atask():
    form = AddTaskFoem(request.form)
    if form.validate():
        url = form.url1.data
        cycle = form.cycle.data
        number = form.number.data
        task = Task(url=url, cycle=IntToString(cycle), number=number, user_id=g.cms_user.id)
        db.session.add(task)
        db.session.commit()
        return field.success(message='添加任务成功！')
    else:
        message = form.get_error()
        return field.params_error(message=message)


# 更新任务
@bp.route('utask/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.POST)
def utask():
    form = UpgradeTaskForm(request.form)
    if form.validate():
        task_id = form.task_id.data
        cycle = form.cycle.data
        number = form.number.data
        url = form.url1.data
        task = Task.query.get(task_id)
        if task:
            '''
            TODO: 代码优化
            '''
            if number == 1:
                task.next_time = None
            else:
                if number > 1:
                    task.next_time = ''
                    for i in range(1, number):
                        a = (datetime.datetime.now() + datetime.timedelta(
                            days=(int((cycle) or 1) * i))).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        if i != number:
                            task.next_time += str(a) + ','
                        else:
                            task.next_time += str(a)
            task.cycle = IntToString(cycle)
            task.url = url
            task.number = number
            db.session.add(task)
            db.session.commit()
            return field.success(message='更新任务成功')
        else:
            return field.params_error(message='未找到该任务')
    else:
        message = form.get_error()
        return field.params_error(message=message)


# 删除任务
@bp.route('dtask/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.POST)
def dtask():
    formm = DeleteTaskForm(request.form)
    if formm.validate():
        task_id = formm.task_id.data
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return field.success(message='删除任务成功')
        else:
            return field.params_error(message='未找到该任务！')
    else:
        message = formm.get_error()
        return field.params_error(message=message)


# cms指纹库管理
@bp.route('cmsmanger/')
@login_required
@permission_required(CMSPersmission.FINGER)
def cmsmanger():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page - 1) * config['development'].BACK_COUNT
    end = start + config['development'].BACK_COUNT
    cmss_obj = Cms_fingerprint.query.order_by(Cms_fingerprint.hit_num.desc(), Cms_fingerprint.create_time.desc())
    cmss = cmss_obj.slice(start, end)
    total = cmss_obj.count()
    pagination = Pagination(bs_version=3, page=page, total=total, outer_window=1, inner_window=1,
                            per_page=config['development'].BACK_COUNT)
    context = {
        'cmss': cmss,
        'pagination': pagination
    }
    return render_template('cms/cms_cmsfinger.html', **context)


# 服务器监控
@bp.route('monitor/')
@login_required
@permission_required(CMSPersmission.SERVER)
def monitor():
    return render_template('cms/cms_monitor.html', async_mode=socketio.async_mode)


# 如何获取monitor传入id?
def get_date():
    while 1:
        date = rediscache.get(1)
        date_list = eval(date)
        socketio.emit('server_response', {'data': date_list}, namespace='/test')
        socketio.sleep(5)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=get_date)


# 增加cms指纹
@bp.route('acms/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.FINGER)
def acms():
    form = AddCmsForm(request.form)
    if form.validate():
        url = form.url.data
        name = form.name.data
        re = form.re.data
        md5 = form.md5.data
        cms = Cms_fingerprint(url=url, name=name, re=re, md5=md5)
        db.session.add(cms)
        db.session.commit()
        return field.success(message='增加成功！')
    else:
        message = form.get_error()
        return field.params_error(message=message)


# 更新cms指纹
@bp.route('ucms/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.FINGER)
def ucms():
    form = UpgradeCmsForm(request.form)
    if form.validate():
        cms_id = form.cms_id.data
        name = form.name.data
        re = form.re.data
        md5 = form.md5.data
        url = form.url.data
        create_time = datetime.datetime.now()
        cms = Cms_fingerprint.query.get(cms_id)
        if cms:
            cms.name = name
            cms.re = re
            cms.md5 = md5
            cms.url = url
            cms.create_time = create_time
            db.session.add(cms)
            db.session.commit()
            return field.success(message='修改成功！')
        else:
            return field.params_error(message='没有改CMS！')
    else:
        message = form.get_error()
        return field.params_error(message=message)


# 删除cms指纹
@bp.route('dcms/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.FINGER)
def dcms():
    form = DeleteCmsForm(request.form)
    if form.validate():
        cms_id = form.cms_id.data
        cms = Cms_fingerprint.query.get(cms_id)
        if cms:
            db.session.delete(cms)
            db.session.commit()
            return field.success(message='删除成功！')
        else:
            return field.params_error(message='没有改CMS！')
    else:
        message = form.get_error()
        return field.params_error(message=message)

#用户管理
@bp.route('usermanger/')
@login_required
@permission_required(CMSPersmission.USERMANGER)
def usermanger():
    roles = CMSRole.query.all()
    users = User.query.all()
    context = {
        'roles': roles,
        'users': users
    }
    return render_template('cms/cms_usermanger.html', **context)


# 添加用户
@bp.route('adduser/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.USERMANGER)
def adduser():
    form = AddUserForm(request.form)
    if form.validate():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        role = form.role.data
        avatar = user_avatar.GithubAvatarGenerator()
        path = '../static/cms/img/user/' + email + '.png'
        avatar.save_avatar(filepath='./static/cms/img/user/' + email + '.png')
        user = User(username=username, password=password, email=email, avatar_path=path)
        db.session.add(user)
        db.session.commit()
        Role = CMSRole.query.filter_by(name=role).first()
        if Role:
            Role.users.append(user)
            db.session.commit()
            return field.success(message='添加用户成功！')
    else:
        message = form.get_error()
        return field.params_error(message=message)


# 管理员管理key
@bp.route('iskey/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.USERMANGER)
def iskey():
    user_id = request.form.get('user_id')
    key = request.form.get('key')
    user = User.query.get(user_id)
    print(user_id, key)
    if user:
        if key == 'down':
            user.is_api = 'ApiEnum.DOWN'
        else:
            user.is_api = 'ApiEnum.UP'
        db.session.add(user)
        db.session.commit()
        return field.success()
    else:
        return field.params_error(message='没有改用户！')


# 修改用户信息
@bp.route('updateuser/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.USERMANGER)
def updateuser():
    form = UpdateUserForm(request.form)
    if form.validate():
        username = form.username.data
        user_id = form.user_id.data
        email = form.email.data
        role = form.role.data
        user = User.query.get(user_id)
        pre_role = user.roles[0].name  # 原有的角色
        if user:
            user.username = username
            user.email = email
            db.session.add(user)
            db.session.commit()

            Role = CMSRole.query.filter_by(name=role).first()
            Pre_Role = CMSRole.query.filter_by(name=pre_role).first()
            if Role:
                Pre_Role.users.remove(user)  # 删除原有的角色
                Role.users.append(user)  # 增加新角色
                db.session.commit()
                return field.success(message='修改信息成功')
        else:
            return field.params_error(message='没有该用户！')
    else:
        message = form.get_error()
        return field.params_error(message=message)


# 禁用用户
@bp.route('stopuser/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.USERMANGER)
def stopuser():
    user_id = request.form.get('user_id')
    status = request.form.get('status')
    if status == 'down':
        is_use = 'UseEnum.UNUSE'
    else:
        is_use = 'UseEnum.USE'
    user = User.query.get(user_id)
    if user:
        user.is_use = is_use
        db.session.add(user)
        db.session.commit()
        return field.success()
    else:
        return field.params_error(message='没有该用户！')


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
            user = User.query.filter_by(email=email).first()
            if user.is_use == 'UseEnum.UNUSE':
                return field.unauth_error(message='该用户已经被禁用，请联系超级管理员解决！')
            if user and user.check_password(password):
                session[config['development'].CMS_USER_ID] = user.id  # 保存用户登录信息
                if remember:
                    # 如果设置session.permanent = True，那么过期时间为31天
                    session.permanent = True
                user.last_login_time = datetime.datetime.now()
                user.is_activate = IntToStatus(1)
                db.session.add(user)
                db.session.commit()
                return field.success(message='登陆成功！')
            else:
                return field.params_error(message='邮箱或者密码错误')

        else:
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


# 生成secretkey
class SecretKey(views.MethodView):
    decorators = [login_required, permission_required(CMSPersmission.POST)]

    def get(self):
        type = request.args.get('type')
        user = g.cms_user
        if type:
            # 生成key
            if type == '1':

                user.secret_key = str(uuid.uuid4())
                db.session.add(user)
                db.session.commit()
                return field.success(message='生成密钥成功！')
            # 删除key
            elif type == '2':
                user.secret_key = ''
                db.session.add(user)
                db.session.commit()
                return field.success(message='删除密钥成功！')
            # 更新密钥
            elif type == '3':
                user.secret_key = str(uuid.uuid4())
                db.session.add(user)
                db.session.commit()
                return field.success(message='更新密钥成功！')
        else:
            return field.params_error(message='没有接收到请求！')


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
bp.add_url_rule('secretkey/', view_func=SecretKey.as_view('secretkey'))
bp.add_url_rule('profile/', view_func=ProFileView.as_view('profile'))
bp.add_app_template_filter(StringToInt, 'To')
bp.add_app_template_filter(StatusToString, 'UPORDOWN')
bp.add_app_template_filter(NoneToString, 'None')
