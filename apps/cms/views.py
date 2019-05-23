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
from pyecharts import Page, Pie
from sqlalchemy import func

from api import field
from config import config
from exts import db, socketio
from models import Cms_fingerprint, Asset
from scan.hostscan.PortScan import host_scan
from scan.webscan.Cms import web_scan
from utils import zlcache, rediscache, avatar as user_avatar
from utils.web_tools import match_url, unabletouch
from .decorators import login_required, permission_required
from .filter import StringToInt, IntToString, IntToStatus, StatusToString, NoneToString, NoneToNone, TitleToShort
from .forms import LoginForm, ResetEmailForm, ResetpwdForm, UpgradeTaskForm, AddTaskFoem, DeleteTaskForm, \
    UpgradeCmsForm, DeleteCmsForm, AddCmsForm, AddUserForm, UpdateUserForm, UpgradeAdminTaskForm, DeleteAdminTaskForm, \
    UusernameForm, UpgradeZcForm
from .models import User, CMSPersmission, Task, CMSRole

thread = None
async_mode = None
thread_lock = Lock()
bp = Blueprint('admin', __name__, url_prefix='/')


# web服务器数据
def webserver(all_count):
    asset_count = all_count
    nginx_count = Asset.query.filter(func.lower(Asset.web_servers).contains('nginx')).count()
    apache_count = Asset.query.filter(func.lower(Asset.web_servers).contains('apache')).count()
    rump_count = Asset.query.filter(func.lower(Asset.web_servers).contains('rump')).count()
    iis_count = Asset.query.filter(func.lower(Asset.web_servers).contains('iis')).count()
    vmserver_count = Asset.query.filter(func.lower(Asset.web_servers).contains('vwebserver')).count()
    other_count = asset_count - (nginx_count + apache_count + iis_count + vmserver_count + rump_count)
    attr_server = ["Nginx", "Apache", "IIS", "RUMP", "VWebserver", "其他"]
    value_server = [nginx_count, apache_count, iis_count, rump_count, vmserver_count, other_count]
    pie = Pie("Web服务器使用情况")
    pie.add("", attr_server, value_server, is_label_show=True, center=[50, 50])
    return pie


# 操作系统数据
def webos():
    linux_count = Asset.query.filter(func.lower(Asset.operating_systems).contains('linux')).count()
    windows_count = Asset.query.filter(func.lower(Asset.operating_systems).contains('windows')).count()
    apple_count = Asset.query.filter(func.lower(Asset.operating_systems).contains('apple')).count()
    waf_count = Asset.query.filter(func.lower(Asset.operating_systems).contains('waf')).count() + Asset.query.filter(
        func.lower(Asset.operating_systems).contains('firewall')).count()
    attr_os = ["Linux", "Windows", "Apple", "Waf"]
    value_os = [linux_count, windows_count, apple_count, waf_count]
    pie = Pie("操作系统使用情况")
    pie.add("", attr_os, value_os, is_label_show=True, center=[50, 50])
    return pie


# 开发语言
def pl():
    php_count = Asset.query.filter(func.lower(Asset.programming_languages).contains('php')).count()
    java_count = Asset.query.filter(func.lower(Asset.programming_languages).contains('java')).count()
    lua_count = Asset.query.filter(func.lower(Asset.programming_languages).contains('lua')).count()
    attr_pl = ["JAVA", "PHP", "LUA"]
    value_pl = [java_count, php_count, lua_count]
    pie = Pie("开发语言使用情况")
    pie.add("", attr_pl, value_pl, is_label_show=True, is_angleaxis_show=True, center=[50, 50])
    return pie


# JS框架
def jsf():
    jquery = Asset.query.filter(func.lower(Asset.javascript_frameworks).contains('jquery')).count()
    right = Asset.query.filter(func.lower(Asset.javascript_frameworks).contains('right')).count()
    Moderniz = Asset.query.filter(func.lower(Asset.javascript_frameworks).contains('modernizr')).count()
    select2 = Asset.query.filter(func.lower(Asset.javascript_frameworks).contains('select')).count()
    lightbox = Asset.query.filter(func.lower(Asset.javascript_frameworks).contains('lightbox')).count()
    attr_jsf = ["jQuery", "RightJs", "Moderniz", "Select2", "LightBox"]
    value_jsf = [jquery, right, Moderniz, select2, lightbox]
    pie = Pie("JS框架使用情况")
    pie.add("", attr_jsf, value_jsf, is_label_show=True, center=[50, 50])
    return pie

#cms
def cms():
    diguo = Asset.query.filter(func.lower(Asset.cms).contains('帝国')).count()
    zhimeng = Asset.query.filter(func.lower(Asset.cms).contains('dede')).count()
    shengda = Asset.query.filter(func.lower(Asset.cms).contains('盛大')).count()
    wiki = Asset.query.filter(func.lower(Asset.cms).contains('hdwiki')).count()
    thinkphp = Asset.query.filter(func.lower(Asset.cms).contains('thinkphp')).count()
    Jee = Asset.query.filter(func.lower(Asset.cms).contains('jee')).count()
    attr_cms = ['帝国CMS','织梦CMS','盛大CMS','HdWiki(中文维基)','ThinkPHP','JeeCMS']
    value_cms = [diguo,zhimeng,shengda,wiki,thinkphp,Jee]
    pie = Pie("CMS使用状况")
    pie.add("", attr_cms, value_cms, is_label_show=True, center=[50,50])
    return pie

#首页
@bp.route('admin/')
@login_required
def index():
    asset_count = Asset.query.count()  # 总资产数
    page = Page()  # 生成页面对象
    # 生成服务器图
    webserver_pie = webserver(asset_count)  # web服务器
    os_pie = webos()  # 操作系统
    pl_pie = pl()  # 开发语言
    jsf_pie = jsf()  # js框架
    cms_pie = cms() #cms
    page.add([webserver_pie, os_pie, pl_pie, jsf_pie, cms_pie])
    return render_template('cms/cms_index.html', chart=page.render_embed(), host='/static/front/js', total=asset_count,
                           script_list=page.get_js_dependencies())

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
        'tasks': tasks,
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
        # TODO:改成前端验证
        if not match_url(url=url):
            return field.params_error(message='URL格式不正确！')
        cycle = form.cycle.data
        number = form.number.data
        task = Task(url=url, cycle=IntToString(cycle), number=number, user_id=g.cms_user.id, referer='WEB')
        db.session.add(task)
        db.session.commit()
        if unabletouch(url=url): #检测url是否可以访问
            if number == 1:
                task.state = 'State.ING_SCAN'
                web_scan.delay(url=url, taskid=task.task_id)
                host_scan.delay(url=url, taskid=task.task_id)
            return field.success(message='添加任务成功！')
        else:#如果不能访问直接返回结果
            task.state = 'State.FINISH_SCAN'
            task.result = str({'status': 'finish','reason':'URL不可达,无法进行扫描'})
            return field.success(message='添加任务完成！')
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
        if not match_url(url=url):
            return field.params_error(message='URL格式不正确！')
        task = Task.query.get(task_id)
        if task:
            '''
            TODO: 代码优化
            '''
            if number == 1:
                web_scan.delay(url=url, taskid=task_id)
                host_scan.delay(url=url, taskid=task_id)
                task.next_time = None
            else:
                if number > 1:
                    task.next_time = ''
                    for i in range(1, number+1):
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
            task.referer = 'WEB'
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
    form = DeleteTaskForm(request.form)
    if form.validate():
        task_id = form.task_id.data
        task = Task.query.get(task_id)
        if task:
            if task.state == 'State.ING_SCAN':
                return field.params_error(message='任务正在进行中，无法删除！')
            db.session.delete(task)
            db.session.commit()
            return field.success(message='删除任务成功')
        else:
            return field.params_error(message='未找到该任务！')
    else:
        message = form.get_error()
        return field.params_error(message=message)


# 查询结果
@bp.route('tresult/')
@login_required
@permission_required(CMSPersmission.POST)
def tresult():
    task_id = request.args.get('task_id')
    if not task_id:
        return field.params_error(message='没有传任务ID')
    task = Task.query.get(task_id)
    if task:
        web_data = task.result
        cms_data = task.cms_result
        host_data = task.host_result
        result = field.result_parse(cms_data, web_data, host_data)
        print(result)
        return field.success(message='查询成功',
                             data={'task_id': task.task_id, 'result_id': task.result_id, 'result': result})
    else:
        return field.params_error(message='没有该任务！')


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
        'pagination': pagination,
        'total': total
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


# 用户查询
@bp.route('queryuser/')
@login_required
@permission_required(CMSPersmission.USERMANGER)
def queryuser():
    name = request.args.get('role')
    is_activate = request.args.get('or')
    print(is_activate, type(is_activate))
    user_list = []
    if name:
        role = CMSRole.query.filter_by(name=name).first()
        if is_activate == '1':
            for user in role.users:
                if user.is_activate == 'LoginEnum.UP':
                    user_list.append(user)
            if len(user_list) ==0:
                return field.success(message='没有找到符合条件的用户!')
            return field.success(message='查询成功！', data={'user': user_list})
        else:
            return field.success(message='查询成功!', data={'user': role.users})
    else:
        if is_activate == '1':
            user = User.query.filter_by(is_activate='LoginEnum.UP').all()
        else:
            user = User.query.filter_by(is_activate='LoginEnum.DOWN').all()
        g.user = user
        return field.success(message='查询成功！')

#管理员任务管理
@bp.route('admintask/')
@login_required
@permission_required(CMSPersmission.ADMINTASK)
def admintask():
    tasks = Task.query.all()
    context = {
        'tasks': tasks
    }
    return render_template('cms/cms_admintask.html', **context)

#管理员更改任务
@bp.route('uadmintask/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.ADMINTASK)
def uadmintask():
    form = UpgradeAdminTaskForm(request.form)
    if form.validate():
        task_id = form.task_id.data
        cycle = form.cycle.data
        number = form.number.data
        url = form.url1.data
        if not match_url(url=url):
            return field.params_error(message='URL格式不正确！')
        task = Task.query.get(task_id)
        if task:
            #TODO: 代码优化
            if number == 1:
                web_scan.delay(url=url, taskid=task_id)
                host_scan.delay(url=url, tasid=task_id)
                task.state = 'State.ING_SCAN'
                task.next_time = None
            else:
                if number > 1:
                    task.next_time = ''
                    for i in range(1, number+1):
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

#管理员删除任务
@bp.route('dadmintask/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.ADMINTASK)
def dadmintask():
    form = DeleteAdminTaskForm(request.form)
    if form.validate():
        task_id = form.task_id.data
        task = Task.query.get(task_id)
        if task:
            if task.state == 'State.ING_SCAN':
                return field.params_error(message='任务正在进行中，无法删除！')
            db.session.delete(task)
            db.session.commit()
            return field.success(message='删除任务成功')
        else:
            return field.params_error(message='未找到该任务！')
    else:
        message = form.get_error()
        return field.params_error(message=message)

#资产页面
@bp.route('zc/')
@login_required
@permission_required(CMSPersmission.ZCMANGAGE)
def zc():
    zcs = Asset.query.all()
    context = {
        'zcs':zcs,
    }
    return render_template('cms/cms_zc.html', **context)

@bp.route('addzc/')
@login_required
@permission_required(CMSPersmission.ZCMANGAGE)
def addzc():
    flag = request.args.get('flag')
    if flag == '1':
        tasks = Task.query.filter_by(state='State.FINISH_SCAN', is_add=1).all()
        number = 0
        db_url_list = []
        to_url_list = []
        assets = Asset.query.all()
        for asset in assets:
            db_url_list.append(asset.url)
        for task in tasks:
            cms = task.cms_result
            web = task.result
            host = task.host_result
            if task.result or task.host_result or task.cms_result:
                result = field.result_parse(cms,web,host)
                if result:
                    try:
                        if task.url not in db_url_list and task.url not in to_url_list:
                            import pymysql
                            asert  = Asset(url=task.url, ip=result.get('ip'), title=result.get('title'), cms=result.get('cms'),operating_systems=str(result.get('os'))
                                           , web_servers=str(result.get('web_server')), programming_languages=str(result.get('programming_languages')),web_frameworks=str(result.get('web_frameworks')),javascript_frameworks=str(result.get('js')), ports=str(result.get(
                                    'port'))
                                           , upgrade_time=datetime.datetime.now(),
                                           header=pymysql.escape_string(str(result.get('header'))),
                                           body=pymysql.escape_string(str(result.get('body'))))
                            db.session.add(asert)
                            db.session.commit()
                            number += 1
                            to_url_list.append(task.url)
                    except Exception as e:
                        pass
        return field.success(message='成功更新{}条资产！'.format(number))
    else:
        return field.params_error(message='没有接受到参数!')

#删除资产
@bp.route('deletezc/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.ZCMANGAGE)
def deletezc():
    zc_id = request.form.get('zc_id')
    if zc_id:
        asset = Asset.query.get(zc_id)
        if asset:
            db.session.delete(asset)
            db.session.commit()
            return field.success(message='删除成功！')
        else:
            return field.params_error(message='没有该条资产信息！')
    return field.params_error(message='没有接受到参数！')

#更新资产
@bp.route('uzc/', methods=['POST'])
@login_required
@permission_required(CMSPersmission.ZCMANGAGE)
def uzc():
    form = UpgradeZcForm(request.form)
    if form.validate():
        zc_id = form.zc_id.data
        type = form.type.data
        text = form.text.data
        asset = Asset.query.get(zc_id)
        if asset:
            if type == '1':
                asset.title=text
            elif type == '2':
                asset.ip = text
            elif type == '3':
                asset.cms = text
            elif type == '4':
                asset.operating_systems = text
            elif type == '5':
                asset.programming_languages = text
            elif type == '6':
                asset.web_servers = text
            elif type == '7':
                asset.web_frameworks = text
            elif type == '8':
                asset.javascript_frameworks = text
            else:
                asset.ports = text
            asset.upgrade_time = datetime.datetime.now()
            db.session.add(asset)
            db.session.commit()
            return field.success('更新成功!')
        return field.params_error(message='没有该资产信息')

    else:
        message = form.get_error()
        return field.params_error(message=message)


#登录
class LoginView(views.MethodView):
    def get(self, message=None):
        return render_template('cms/login.html', message=message)

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data  # 邮箱或者用户名
            password = form.password.data
            remember = form.remember.data
            user = User.query.filter_by(email=email).first() or User.query.filter_by(username=email).first()
            if user:
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


# 修改昵称
@bp.route('uusername/', methods=['POST'])
@login_required
def uusername():
    form = UusernameForm(request.form)
    if form.validate():
        username = form.username.data
        user = g.cms_user
        user.username = username
        db.session.add(user)
        db.session.commit()
        return field.success()
    else:
        message = form.get_error()
        return field.params_error(message=message)


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
bp.add_app_template_filter(NoneToNone, 'Zero')
bp.add_app_template_filter(TitleToShort, 'Title')
