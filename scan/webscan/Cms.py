# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

import hashlib
import math
import queue
import re
import threading
import time

import builtwith
import redis
import requests

import pymysql
from config import config
from web_scan_task import web_celery_app
from .Waf_Server_Language import WebEye
from ..dosql import Mysql

config = config['development']

redisConn = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)


def AverageSplit(L, index):
    """
    Average split list
    """
    count = len(L)
    return [L[(i - 1) * index:i * index] for i in list(range(1, math.ceil(count / index) + 1))]


def getMD5(c):
    m = hashlib.md5()
    m.update(c)
    psw = m.hexdigest()
    return psw


def success(tmp, taskid):
    # 成功后先将结果更新到w11scan_config result表中，更新信息，然后更新w11scan表中指纹命中率

    # tmp {'_id': ObjectId('5b5f48158598842b975e03a8'), 'path': '/robots.txt', 'option': 'regx', 'content': 'wordpress','hit': 0, 'name': 'wordpress'}

    # 1.插入成功信息到w11scan_config resutl表中
    mysql = Mysql()
    tmp['option'] = ('re' if tmp.get('re') !='' else 'md5')
    data = {
        "status": "success",
        "webdna": {
            "cmsname": tmp.get("name"),
            "path": tmp.get("path"),
            "option": tmp['option'],
            "content": tmp[tmp['option']],
            "dnaid": tmp["id"],
            "time": time.time()
        }
    }

    mysql.sql("UPDATE `task` SET `state`='State.FINISH_SCAN', `cms_result`=\"{}\" WHERE `task_id`='{}'".format(str(data), taskid))
    print(2222222)

    # 2. 更新指纹命中率
    dnaid = tmp.get('id')
    mysql.sql("UPDATE `cms_fingerprint` SET `hit_num`=`hit_num`+1 WHERE `id` = '{}'".format(dnaid))



# 这只是预处理模块，不涉及扫描和判断部分
class whatweb(object):

    def __init__(self,urls):
        self.mysql = Mysql()
        self.urls = urls
        self.cms_hash_list = {}

    def buildPayload(self):
        collections = self.mysql.query(table='cms_fingerprint', order='hit_num')
        path_cache_hit = []
        for i in collections:
            try:
                name = i[2]
                path = i[1]
                id = str(i[0])
                hit = i[6]
                re = i[3]
                md5 = i[4]
                if path not in self.cms_hash_list:
                    self.cms_hash_list[path] = []
                cms = {'id':id, 'name':name, 'path':path, 'hit':hit, 're':re, 'md5':md5}
                self.cms_hash_list[path].append(cms)
                if str(i[6]).isdigit() and int(i[6]) > 0:
                    path_cache_hit.append((path, int(i[6])))
            except:
                continue

        # 组合指纹

        cms_key_cache = {}
        for k, v in self.cms_hash_list.items():
            cms_key_cache[k] = len(v)

        # 路径排名前十 [('/favicon.ico', 68), ('/robots.txt', 31), ('', 21), ('/license.txt', 6)
        pathList = sorted(cms_key_cache.items(), key=lambda d: d[1], reverse=True)

        # 按照路径进行排序，然后取出命中率前十的路径的指纹排序在前面。
        # [('/images/buttonImg/add.png', 1)]
        pathL = sorted(path_cache_hit, key=lambda x: x[1],reverse=True)[:10]

        # build OrderDict
        combine = []
        for item in pathL + pathList:
            if item[0] not in combine:
                combine.append(item[0])
        # print(AverageSplit(combine, 10))
        return AverageSplit(combine,10)

    def run(self):
        items = self.buildPayload()
        webList = []
        for item in items:
            # webDict = c1.OrderedDict()
            webDict = []
            for i in item:
                # webDict[i] = self.cms_hash_list[i]
                webDict.append(self.cms_hash_list[i])
            webList.append(webDict)
        return webList


# 分布式扫描程序,接收url和payload,一次接受多个payload,启动线程池消费
class WhatScan(object):

    def __init__(self, url, payload, taskid, threadnum=100):
        self.queue = queue.Queue()
        self.threadNum = threadnum
        self.threadContinue = True
        self.domain = url
        self.taskid = taskid
        for i in payload:
            self.queue.put(i)
        self.result = []

    def exceptionHandledFunction(self):
        while not self.queue.empty() and self.threadContinue:

            payload = self.queue.get()
            # payload like [{'_id': ObjectId('5b5f48158598842b975e03a8'), 'path': '/robots.txt', 'option': 'regx','content': 'wordpress', 'hit': 0, 'name': 'wordpress'}
            if isinstance(payload, list) and len(payload):
                path = payload[0]["path"]
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
                }
                self.domain = self.domain.strip('/')
                new_url = self.domain + path
                try:
                    r = requests.get(new_url, headers=headers)
                except:
                    print("error:" + new_url)
                    continue
                if r.status_code == 200:
                    bytes = r.content
                    html = r.text
                    for tmp in payload:
                        recontext = tmp.get('re')
                        md5 = tmp.get('md5')
                        tmp["url"] = self.domain
                        fingter = False

                        if md5:
                            if md5 == getMD5(bytes):
                                fingter = True
                        if recontext:
                            r = re.search(recontext, html)
                            if r:
                                fingter = True
                        if fingter:
                            self.result.append(tmp)
                            redisConn.delete(self.domain)
                            success(tmp, self.taskid)


    def run(self):

        threads = []
        for numThread in list(range(self.threadNum)):
            thread = threading.Thread(target=self.exceptionHandledFunction, name=str(numThread), args=[])
            thread.daemon = True
            thread.start()
            threads.append(thread)

        # And wait for them to all finish
        alive = True
        while alive:
            alive = False
            for thread in threads:
                if thread.isAlive():
                    alive = True
                    time.sleep(0.1)

        if len(self.result) == 0:
            return False
        return self.result


@web_celery_app.task
def otherscan(url, taskid):
    try:
        res = WebEye(url)
        res.run()
        cms = res.cms_list
        title = res.title()
        header = res.header()
        body = res.body()
        try:
            build = builtwith.builtwith(url)
        except:
            build = {}
        if cms:
            build["other"] = cms

        data = {
            "status": "finish",
            "other": build,
            "title": title,
            "header": header,
            # 'body': body,
        }
        Mysql().sql("UPDATE `TASK` SET `state`='State.FINISH_SCAN', `result`=\"{}\" WHERE `task_id`='{}'".format(pymysql.escape_string(str(data)), taskid))
        print(111111)
    except:
        Mysql().sql("UPDATE `TASK` SET `state`='State.FINISH_SCAN', `result`='' WHERE `task_id`='{}'".format(taskid))


@web_celery_app.task
def web_scan(url, taskid):
    what = whatweb(url)
    redisConn.set(url, "1", ex=60 * 60 * 24)
    wli = what.run()
    for ordict in wli:
        singscan.delay(url, ordict, taskid)
    otherscan.delay(url, taskid)
    # other


@web_celery_app.task
def singscan(url, ordict, taskid):
    value = redisConn.get(url)
    if value is None or value != "1":
        return False
    scan = WhatScan(url, ordict, taskid)
    l = scan.run()
    return l


if __name__ == '__main__':
    url = "https://x.hacking8.com"
