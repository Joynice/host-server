# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import json

import requests
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app
from config import config
from exts import db
from models import Cms_fingerprint, TestWebsite, Asset
from apps.cms import models as cms_models
from utils.avatar import GithubAvatarGenerator

app = create_app()
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)
User = cms_models.User
Role = cms_models.CMSRole
Permission = cms_models.CMSPersmission

# 将本地指纹库上传数据库
@manager.command
def add_cms_fingerprint():
    fp = open(config['development'].CMS_FINGERPRINT, 'rb')
    CmsData = json.load(fp, encoding="utf-8")
    for i in CmsData:
        cms = Cms_fingerprint(url=i.get('url'), re=i.get('re'), name=i.get('name'), md5=i.get('md5'))
        db.session.add(cms)
    print('添加成功！')
    db.session.commit()

@manager.command
def add_test_cms():
    fp = open(config['development'].TEST_CMS_SITE, 'rb')
    TestData = json.load(fp, encoding="utf-8")
    for i in TestData:
        try:
            req = requests.get(i.get('manufacturerUrl'), headers = config['development'].HRADER)
            if req.status_code == 200:
                if i.get('recognitionType_id') == 1:
                    print(i)
                    cms = TestWebsite(manufacturerUrl=i.get('manufacturerUrl'), manufacturerName=i.get('manufacturerName'),
                                      name=i.get('program_name'), url=i.get('url'), md5=i.get('recognition_content'))
                else:
                    cms = TestWebsite(manufacturerUrl=i.get('manufacturerUrl'), manufacturerName=i.get('manufacturerName'),
                                      name=i.get('program_name'), url=i.get('url'), re=i.get('recognition_content'))
                db.session.add(cms)
                db.session.commit()
        except:
            pass

'''
添加后台用户
'''
@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
@manager.option('-e', '--email', dest='email')
def create_cms_user(username, password, email):
    avatar = GithubAvatarGenerator()
    path = '../static/cms/img/user/'+ email +'.png'
    avatar.save_avatar(filepath='./static/cms/img/user/'+ email +'.png')
    user = User(username=username, password=password, email=email, avatar_path=path)
    db.session.add(user)
    db.session.commit()
    print('cms用户添加成功')

'''
创建角色
'''
@manager.command
def create_role():
    # 1. 访问者（可以修改个人信息）
    visitor = Role(name='访问者', desc='只能访问数据，不能修改。')
    visitor.permissions = Permission.VISITOR
    # 2.普通用户（可以下发任务，查询任务结果。）
    user = Role(name='普通用户', desc='可以下发任务，查询任务结果。')
    user.permissions = Permission.VISITOR | Permission.POST
    # 3.管理员（拥有绝大多数权限）
    admin = Role(name='管理员', desc='拥有本系统大部分权限。')
    admin.permissions = Permission.VISITOR | Permission.POST | Permission.MANAGER | Permission.FINGER |Permission.ZCMANGAGE

    # 4.超级管理员
    superadmin = Role(name='超级管理员', desc='拥有本系统所有权限。')
    superadmin.permissions = Permission.ALL_PERMISSON

    # 5.开发者
    developer = Role(name='开发者', desc='开发者专用角色。')
    developer.permissions = Permission.ALL_PERMISSON

    db.session.add_all([visitor, user, admin, developer, superadmin])
    print('添加完成')
    db.session.commit()

'''
测试
'''
@manager.command
def test_permission():
    user = User.query.first()
    if user.has_permission(Permission.VISITOR):
        print('这个角色有访问者权限！')
    else:
        print('这个角色没有访问者权限！')

'''
给用户添加角色
'''
@manager.option('-e', '--email', dest='email')
@manager.option('-n', '--name', dest='name')
def add_user_to_role(email, name):
    user = User.query.filter_by(email=email).first()
    if user:
        role = Role.query.filter_by(name=name).first()
        if role:
            role.users.append(user)
            db.session.commit()
            print('用户添加到角色成功!')
        else:
            print('没有这个角色：{}'.format(role))
    else:
        print('{}：这个邮箱没有被注册'.format(email))

if __name__ == '__main__':
    manager.run()