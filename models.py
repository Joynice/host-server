# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
'''
主要存放资产模型
'''
from exts import db
import datetime


class Asset(db.Model):
    '''
    资产类
    '''
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    webapp = db.Column(db.String(255))
    os = db.Column(db.String(255))
    server = db.Column(db.String(255))
    framework = db.Column(db.String(255))
    component = db.Column(db.String(255))
    waf = db.Column(db.String(255))
    cms = db.Column(db.String(255))
    url = db.Column(db.String(255), unique=True)
    upgrade_time = db.Column(db.DateTime, default=None)


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
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    hit_num = db.Column(db.Integer, default=0, nullable=False)


class TestWebsite(db.Model):
    '''
    测试网站
    '''
    __tablename__ = 'test_website'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    manufacturerUrl = db.Column(db.String(255), nullable=False)
    manufacturerName = db.Column(db.String(50))
    name = db.Column(db.String(50))
    url = db.Column(db.String(255), nullable=False)
    re = db.Column(db.String(255))
    md5 = db.Column(db.String(255))