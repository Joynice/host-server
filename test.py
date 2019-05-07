import math
from webscan.dosql import Mysql
import math

from webscan.dosql import Mysql


# class MongDB(object):
#     def __init__(self,database = 'w11scan'):
#         self.host = '127.0.0.1'
#         self.port = 27017
#         self.database = database
#         self.conn = MongoClient(self.host,self.port)
#         self.coll = self.conn[self.database]


def AverageSplit(L,index):
    """
    Average split list
    """
    count = len(L)
    return [L[(i - 1) * index:i * index] for i in list(range(1, math.ceil(count / index) + 1))]

class whatweb(object):

    def __init__(self,urls):
        self.mysql = Mysql()
        self.urls = urls
        self.cms_hash_list = {}

    def buildPayload(self):
        collections = self.mysql.query(table='cms_fingerprint')
        path_cache_hit = []
        for i in collections:
            try:
                name = i[2]
                path = i[1]
                id = str(i[0])
                hit = i[6]
                re = i[3]
                md5 = i[4]
                print(name,path,id)
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
        print(AverageSplit(combine, 10))
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

if __name__ == '__main__':
    a = whatweb(urls=['https://www.baidu.com']).run()
    print(a)