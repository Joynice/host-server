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
        self.cursor = self._create_cursor()

    #创建游标
    def _create_cursor(self):
        return self.db.cursor()

    #查询数据
    def query(self, table='task', obj='*', factor=None, num='all', order=None):
        '''
        :param table: 表名
        :param obj: 查询对象（默认所有）
        :param factor: 条件（默认无）
        :param num: 全部or第一个（默认所有）
        :return: 查询结果
        '''
        if  not factor:
            if not order:
                sql = "SELECT {} FROM {}".format(obj, table)
            else:
                sql = "SELECT {} FROM {} ORDER BY {} DESC".format(obj, table,order)
        else:
            if not order:
                sql = "SELECT {} FROM {} WHERE {}".format(obj, table, factor)
            else:
                sql = "SELECT {} FROM {} WHERE {} ORDER BY {} DESC".format(obj, table, factor, order)
        try:
            print(sql)
            self.cursor.execute(sql)
            if num=='all':
                res = self.cursor.fetchall()
            else:
                res = self.cursor.fetchone()
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
                self.db.ping(reconnect=True)
                self.cursor.execute(sql)
                self.db.commit()
                self.cursor.close()
                self.closedb()
                return 1
            except Exception as e:
                print(e)
                self.db.ping(reconnect=True)
                self.db.rollback()
                self.closedb()
                return 0

    # 删除数据
    def delete(self, table='task', factor=None):
        '''
        :param table:表名
        :param factor: 条件（默认无）
        :return:
        '''
        if not factor:
            sql = 'DELETE FROM {}'.format(table)
        else:
            sql = 'DELETE FROM {} WHERE {}'.format(table, factor)
        try:
            self.db.ping(reconnect=True)
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        self.closedb()

    def sql(self, sql):
        if sql:
            try:
                self.db.ping(reconnect=True)
                self.cursor.execute(sql)
                self.db.commit()
            except Exception as e:
                print(e)
                print(sql)
                self.db.rollback()
            self.closedb()

    #关闭会话
    def closedb(self):
        self.db.close()

if __name__ == '__main__':
    mysql = Mysql()
    a = mysql.query(table='task', obj='state', factor='task_id="dz2UN5WxjwNBABGnmAm9nk"', num='one')
    print(a)