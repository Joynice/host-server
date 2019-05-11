# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import datetime
import time
from scan.dosql import Mysql
from scan.hostscan.PortScan import host_scan
from scan.webscan.Cms import web_scan
from config import config
config = config['development']


class CycleScan(object):
    def __init__(self):
        self.mysql = Mysql()
    def scan(self):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.now().hour
        tasks = self.mysql.query(factor='`number` > 1', num='all')
        if len(tasks) >= 1: #如果有周期任务继续进行
            for task in tasks: #遍历每一个任务
                next_time = task[6] #获得对应数据库里next_time字段
                if ',' in next_time: #判断'，'是否在里面，因为存数据时用','进行分割
                    next_time_list = next_time.split(',')#如果有的话，转化成列表
                else:#如果没有next_time可能只有一个时间或者没有
                    next_time_list = []
                    next_time_list.append(next_time)#将时间添加进去
                if len(next_time_list)>=1:#排除没有时间的情况
                    first_time = datetime.datetime.strptime(next_time_list[0], '%Y-%m-%d %H:%M:%S') #将列表里面一个时间格式转化成data对象
                    if first_time.year==year and first_time.month==month and first_time.day==day and first_time.hour==hour: #判断年月日时
                        url = task[3] #获得url
                        task_id = task[1] #获得task_id
                        host_scan.delay(url=url, taskid=task_id) #主机扫描
                        web_scan.delay(url=url, taskid=task_id) #端口扫描
                        del next_time_list[0] #删除第一个时间
                        new_time = ','.join(next_time_list) #更新数据库next_time字段
                        print(task_id)
                        self.mysql.sql("UPDATE `task` SET `next_time`='{}' WHERE `task_id`='{}'".format(new_time, task_id))

    def run(self):
        self.scan()

if __name__ == '__main__':
    while True:
        cycle_scan = CycleScan()
        cycle_scan.run()
        time.sleep(config.CYCLE_SCAN_TIME*60)
