# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from exts import db
import enum
import datetime
import shortuuid
from werkzeug.security import generate_password_hash, check_password_hash


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
    asset = db.relationship('Asset', uselist=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('number') > 1:
            self.next_time = ''
            for i in range(1, kwargs.get('number') + 1):
                print(i)
                a = (datetime.datetime.now() + datetime.timedelta(days=(int((kwargs.get('cycle')) or 1) * i))).strftime(
                    '%Y-%m-%d %H:%M:%S')
                if i != kwargs.get('number'):
                    self.next_time += str(a) + ','
                else:
                    self.next_time += str(a)
        super(Task, self).__init__(*args, **kwargs)


class User(db.Model):
    '''
    用户类
    '''
    __tablename__ = 'user'
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    telephone = db.Column(db.String(11), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    _password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True)
    realname = db.Column(db.String(20))
    avatar = db.Column(db.String(100))
    signature = db.Column(db.String(100))
    gender = db.Column(
        db.Enum(str(GenderEnum.MALE), str(GenderEnum.FEMALE), str(GenderEnum.SECRET), str(GenderEnum.UNKNOW)),
        default=str(GenderEnum.UNKNOW))
    join_time = db.Column(db.DateTime, default=datetime.datetime.now)

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


class Asset(db.Model):
    '''
    资产类
    '''
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    webapp = db.Column(db.String(255))
    os = db.Column(db.String(255))
    server = db.Column(db.String(255))
    framework = db.Column(db.String(255))
    component = db.Column(db.String(255))
    waf = db.Column(db.String(255))
    cms = db.Column(db.String(255))
    url = db.relationship('Task')


class Cms_fingerprint(db.Model):
    '''
    cms指纹
    '''
    __tablename__ = 'cms_fingerprint'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(255))
    name = db.Column(db.String(100), nullable=False)
    re = db.Column(db.String(100))
    md5 = db.Column(db.String(255))
