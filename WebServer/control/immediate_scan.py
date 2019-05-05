# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import queue
from WebServer.dosql import Mysql

class ImmediateScan(object):
    def __init__(self):
        self.TaskQueue = queue.Queue()
        self.LogQueus = queue.Queue()
        self.ResultQusus = queue.Queue()
        self.db = Mysql()

    def get_task(self):
        task = self.db.query(factor='number=1')
        if task:
            print(task)

    def run(self):
        pass

if __name__ == '__main__':
    a = ImmediateScan().get_task()
