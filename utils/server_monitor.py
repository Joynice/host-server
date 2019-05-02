# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import psutil
import redis
from threading import Lock
import time
from config import config

host = config['development'].REDIS_HOST
port = config['development'].REDIS_PORT
db = config['development'].REDIS_MONITOR_DB
r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
thread = None
thread_lock = Lock()


def set(key, value):
    return r.set(key, value=value)


def rpush(key, value):
    return r.lpushx(key, value)


def get_key():
    keys = psutil.net_io_counters(pernic=True).keys()
    recv = {}
    sent = {}
    for key in keys:
        recv.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_recv)
        sent.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_sent)
    return keys, recv, sent


def xx(keys, old_recv, old_sent, now_recv, now_sent):
    net_in = {}
    net_out = {}
    for key in keys:
        net_in.setdefault(key, (now_recv.get(key) - old_recv.get(key)) / 1024)
        net_out.setdefault(key, (now_sent.get(key) - old_sent.get(key)) / 1024)
    sxll = 0
    xxll = 0
    for key in keys:
        sxll += net_out.get(key)
        xxll += net_in.get(key)
    return sxll, xxll, (sxll + xxll)


# 后台线程 产生数据，即刻推送至前端
def background_thread():
    count = 0
    while True:
        keys, old_recv, old_sent = get_key()
        time.sleep(5)
        keys, now_recv, now_sent = get_key()
        net_in, net_out, net_all = xx(keys, old_recv, old_sent, now_recv, now_sent)
        # print(net_in, net_out, net_all)

        count += 1
        t = time.strftime('%Y-%m-%d %H:%M:%S')
        # 获取系统时间（只取分:秒）
        cpus = psutil.cpu_percent(interval=None, percpu=False)
        print(cpus)
        process = psutil.virtual_memory().percent
        # 获取系统cpu使用率 non-blocking
        return str([t, cpus, process, net_out / 5, net_in / 5, net_all / 5])


if __name__ == '__main__':

    while True:
        date = background_thread()
        print(date)
        datas = {'server': 1, 'date': date}
        set(key=datas.get('server'), value=date)