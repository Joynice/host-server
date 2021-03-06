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
    web_servers = db.Column(db.String(255))
    javascript_frameworks = db.Column(db.String(255))
    programming_languages = db.Column(db.String(255))
    web_frameworks = db.Column(db.String(255))
    operating_systems = db.Column(db.String(255))
    cms = db.Column(db.String(255))
    url = db.Column(db.String(255), unique=True)
    ip = db.Column(db.String(255))
    ports = db.Column(db.Text)
    title = db.Column(db.String(255))
    other = db.Column(db.Text(16777216))
    header = db.Column(db.Text(16777216))
    body = db.Column(db.Text(16777216))
    upgrade_time = db.Column(db.DateTime, default=None)
    statue = db.Column(db.Integer, default=0, nullable=False)


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