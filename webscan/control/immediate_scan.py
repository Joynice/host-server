# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from webscan.dosql import Mysql
from tasks import cms
from multiprocessing import queues

class ImmediateScan(object):
    def __init__(self):
        self.TaskQueue = queues.Queue()
        self.LogQueus = queues.Queue()
        self.ResultQusus = queues.Queue()
        self.db = Mysql()

    def get_task(self):
        task = self.db.query(factor='number=1')
        if task:
            for i in task:
                task_id = i[1]
                url = i[3]
                cms.delay(url=url)

    def run(self):
        pass

if __name__ == '__main__':
    a = ImmediateScan().get_task()
