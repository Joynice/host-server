# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from exts import db
import enum
import datetime
import shortuuid
from werkzeug.security import generate_password_hash, check_password_hash
from .filter import StringToInt
import os
sep = os.sep
import random

'''
主要存放用户模型以及任务模型
'''

class Cycle(enum.Enum):
    ONEDAY = 1
    THREEDAY = 3
    WEEK = 7
    HALF_MONTH = 15
    ONEMONTH = 30


class State(enum.Enum):
    WAIT_SCAN = 0
    ING_SCAN = 1
    FINISH_SCAN = 2


class GenderEnum(enum.Enum):
    MALE = 1
    FEMALE = 2
    SECRET = 3
    UNKNOW = 4

class CMSPersmission(object):
    #所有权限
    ALL_PERMISSON = 0b11111111
    #访问者权限
    VISITOR = 0b00000001
    #管理自己任务
    POST = 0b00000010
    #管理所有任务
    MANAGER = 0b00000100
    #指纹管理
    FINGER = 0b00001000
    #资产管理
    ZCMANGAGE = 0b00010000
    #管理员任务系统
    ADMINTASK = 0b00100000
    #服务器监控
    SERVER = 0b01000000
    #用户管理
    USERMANGER = 0b10000000


cms_role_user = db.Table(
    'cms_role_user',
    db.Column('cms_role_id', db.Integer, db.ForeignKey('cms_role.id'), primary_key=True),
    db.Column('cms_user_id', db.String(100), db.ForeignKey('user.id'), primary_key=True),
)

class User(db.Model):
    '''
    用户类
    '''
    __tablename__ = 'user'
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    telephone = db.Column(db.String(11), unique=True)
    username = db.Column(db.String(50), nullable=False)
    _password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True)
    realname = db.Column(db.String(20))
    avatar_path = db.Column(db.String(100))
    signature = db.Column(db.String(100))
    gender = db.Column(
        db.Enum(str(GenderEnum.MALE), str(GenderEnum.FEMALE), str(GenderEnum.SECRET), str(GenderEnum.UNKNOW)),
        default=str(GenderEnum.UNKNOW))
    join_time = db.Column(db.DateTime, default=datetime.datetime.now)
    secret_key = db.Column(db.String(100))
    tasks = db.relationship('Task', backref='user', lazy=True)

    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            self.password = kwargs.get('password')
            kwargs.pop('password')
        super(User, self).__init__(*args, **kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, newpwd):
        self._password = generate_password_hash(newpwd)

    def check_password(self, rawpwd):
        return check_password_hash(self._password, rawpwd)

    @property
    def permissions(self):
        if not self.roles:
            return 0
        all_permissions = 0
        for role in self.roles:
            permissions = role.permissions
            all_permissions |= permissions
        return all_permissions

    def has_permission(self, permission):
        return self.permissions & permission == permission

    @property
    def is_developer(self):
        return self.has_permission(CMSPersmission.ALL_PERMISSON)


    def avatar(self):
        print(sep + 'static' + sep + 'cms' + sep + 'img' + sep + 'default' + sep + random.choice(
            os.listdir('./static/cms/img/default/')))
        return sep + 'static' + sep + 'cms' + sep + 'img' + sep + 'default' + sep + random.choice(
            os.listdir('./static/cms/img/default/'))



class CMSRole(db.Model):
    __tablename__ = 'cms_role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now())
    permissions = db.Column(db.Integer, default=CMSPersmission.VISITOR)
    # 多对多的关系，通过中间表联系，需要关系的对象'CMSUser',中间表'secondary',反向引用'backref'
    users = db.relationship('User', secondary=cms_role_user, backref='roles')


class Task(db.Model):
    '''
    创建任务类
    '''
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String(255), default=shortuuid.uuid)
    result_id = db.Column(db.String(255), default=shortuuid.uuid)
    url = db.Column(db.String(255), nullable=False)
    cycle = db.Column(
        db.Enum(str(Cycle.ONEDAY), str(Cycle.THREEDAY), str(Cycle.WEEK), str(Cycle.HALF_MONTH), str(Cycle.ONEMONTH)),
        default=str(Cycle.ONEDAY))
    task_time = db.Column(db.DateTime, default=datetime.datetime.now)
    next_time = db.Column(db.String(1000), nullable=True)
    number = db.Column(db.Integer, default=1)
    state = db.Column(db.Enum(str(State.WAIT_SCAN), str(State.ING_SCAN), str(State.FINISH_SCAN)),
                      default=str(State.WAIT_SCAN))
    result = db.Column(db.Text, nullable=True)
    html = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'))

    def __init__(self, *args, **kwargs):
        if kwargs.get('number') > 1:
            self.next_time = ''
            print(kwargs.get('cycle'))
            for i in range(1, kwargs.get('number')):
                a = (datetime.datetime.now() + datetime.timedelta(days=(int(StringToInt(kwargs.get('cycle')) or 1) * i))).strftime(
                    '%Y-%m-%d %H:%M:%S')
                if i != kwargs.get('number'):
                    self.next_time += str(a) + ','
                else:
                    self.next_time += str(a)
        super(Task, self).__init__(*args, **kwargs)
