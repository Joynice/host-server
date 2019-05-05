# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

import pymysql
from config import config
config = config['development']

class Mysql(object):
    def __init__(self, host=config.MYSQL_HOST, port=config.MYSQL_PORT, username=config.MYSQL_USERNAME, password=config.MYSQL_PASSWORD, db=config.MYSQL_DATABASE):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db = pymysql.connect(host, username, password, db)

    #创建游标
    def _create_cursor(self):
        return self.db.cursor()

    #查询数据
    def query(self, table='task', obj='*', factor=None, num='all'):
        '''

        :param table: 表名
        :param obj: 查询对象（默认所有）
        :param factor: 条件（默认无）
        :param num: 全部or第一个（默认所有）
        :return: 查询结果
        '''
        if  not factor:
            sql = "SELECT {} FROM {}".format(obj, table)
        else:
            sql = "SELECT {} FROM {} WHERE {}".format(obj, table, factor)
        cursor = self._create_cursor()
        try:
            cursor.execute(sql)
            if num=='all':
                res = cursor.fetchall()
            else:
                res = cursor.fetchone()
            return res
        except Exception as e:
            print(e)

    #更新数据
    def update(self, table='task', factor=None, obj=None):
        '''
        :param table: 表名
        :param factor: 条件（默认无）
        :param obj: 更新对象（这个参数必须有）
        :return:
        '''
        if obj == None:
            return 0
        else:
            if not factor:
                sql = 'UPDATE {} SET {}'.format(table, obj)
            else:
                sql = 'UPDATE {} SET {} WHERE {}'.format(table, obj, factor)
            try:
                cursor = self._create_cursor()
                cursor.execute(sql)
                self.db.commit()
                self.closedb()
                return 1
            except:
                self.db.rollback()
                self.closedb()
                return 0

    def delete(self, table='task', factor=''):
        pass








    #关闭会话
    def closedb(self):
        self.db.close()






