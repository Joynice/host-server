# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import gevent
from gevent import monkey
monkey.patch_all()
import os
import json
import hashlib
import requests
from colorama import init, Fore
from gevent.queue import Queue
from app import create_app
from config import config
from models import Asset

app = create_app()

init(autoreset=True)

class CmsInfo(object):
    def __init__(self, desurl, is_internet=True, thread=100, whatweb=False, file=None):
        self.file = file
        self.flag = True
        self.desurl = desurl
        self.thread = thread
        self.whatweb = whatweb
        self.IsInternet = is_internet
        self.res = Queue()  # 结果队列
        self.message = Queue()  # 消息队列
        self.UrlQueue = Queue()  # 目标队列
        self.location = Queue()  # 指纹队列
        self.header1 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
                        'Content-Type': 'application/x-www-form-urlencoded'}
        self.header2 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'}

    # Url组成队列
    def UrlMake2Queue(self):
        if self.desurl is not None:
            self.UrlQueue.put(self.desurl.strip('/'))
            return True
        if self.file is not None:
            if not os.path.exists(self.file):
                print(Fore.RED + '[Error]:File not found')  # 文件不存在
            else:
                try:
                    target = open(self.file, 'r')
                    lines = target.readlines()
                    for line in lines:
                        self.UrlQueue.put(line.strip().strip('/'))
                    target.close()
                    return True
                except BaseException as e:
                    print(Fore.RED + '[Error]:File %s open filed\n%s' % (self.file, e))  # 文件打开失败
                    exit()

    # 将本地指纹组成队列
    def CmsMake2Queue(self):
        fp = open(config['development'].CMS_FINGERPRINT, 'rb')
        CmsData = json.load(fp, encoding="utf-8")
        for i in CmsData:
            self.location.put(i)
        fp.close()

    # 清空队列
    def CleaerQueue(self):
        while not self.location.empty():
            self.location.get()

    # 获取MD5
    def GetMd5(self, repfile):
        md5 = hashlib.md5()
        md5.update(repfile)
        return md5.hexdigest()

    # 使用指纹识别CMS
    def Get2Location(self, url):
        while not self.location.empty():
            CmsJson = self.location.get()
            FinalUrl = url + CmsJson['url']
            print(Fore.CYAN + '[Message]: %s' % FinalUrl)
            RspHtmlC = ''
            try:
                rsp = requests.get(FinalUrl, headers=self.header2, timeout=3)
                if rsp.status_code != 200:
                    continue
                RspHtmlC = rsp.text
                RspHtmlC1 = rsp.content
                if RspHtmlC is None:
                    continue
            except BaseException as e:
                RspHtmlC = ''
                self.message.put({'error': 'Network anomalies or Program error. On: Get2Location. URL:%s\n%s' % (
                    url, e)})  # 网络异常或者程序出错,抛出异常,目的域名
                continue
            if CmsJson['re']:
                if RspHtmlC.find(CmsJson['re']) != -1:
                    self.res.put({'LocResult': 'Target cms is : %s Source : %s KeyWord : %s' % (
                        CmsJson['name'], url, CmsJson['re'])})
                    print(Fore.GREEN + '[LocResult]: Target cms is : %s Source : %s KeyWord : %s' % (
                        CmsJson['name'], url, CmsJson['re']))
                    self.CleaerQueue()
                    return True
            else:
                md5 = self.GetMd5(RspHtmlC1)
                if md5 == CmsJson['md5']:
                    self.res.put({'LocResult': 'Target cms is : %s Source : %s KeyWord : %s' % (
                        CmsJson['name'], url, CmsJson['md5'])})
                    print(Fore.GREEN + '[LocResult]: Target cms is : %s Source : %s KeyWord : %s' % (
                        CmsJson['name'], url, CmsJson['md5']))
                    self.CleaerQueue()
                    return True

    # 从http://whatweb.bugscaner.com/look/ 获取cms指纹信息，每次只能查询100次
    def Get2Internet(self, url):
        if self.IsInternet:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            post = {
                'hash': '0eca8914342fc63f5a2ef5246b7a3b14_7289fd8cf7f420f594ac165e475f1479',
                'url': url
            }
            if self.flag:
                try:
                    info = requests.post(url='http://whatweb.bugscaner.com/what/', data=post, headers=headers).text
                    print(info)
                    if info['error'] == 'no':
                        # 结果返回正常
                        s = ''
                        s = 'Cms: [' + info['CMS'] + '] Other: {'
                        for k, v in info.items():
                            if k != 'url' and k != 'error' and k != 'CMS':
                                for target_list in v:
                                    s = s + k + ': [' + target_list + '] '
                        s = s + '} Url: [' + info['url'] + ']'
                        self.res.put({'InterResult': info})
                        print(Fore.GREEN + '[InterResult]: ' + s)
                        return True
                        # 结果返回犯错 对返回的错误进行处理
                    if info['error'] == '1':
                        self.message.put({'error': 'Domain cannot be accessed. Url: %s' % (url)})  # 域名不能访问
                        # print(Fore.RED + '[Error]: Domain cannot be accessed. Url: %s' % (url))
                        return False
                    if info['error'] == '2':
                        self.message.put({'info': 'More than 100 queries. Url: %s' % (url)})  # 查询次数超过100次
                        # print(Fore.YELLOW + '[Info]: More than 100 queries. Url: %s' % (url))
                        self.flag = False
                        return False
                    if info['error'] == '3':
                        self.message.put({'unres': 'Not recognized.Url: %s' % (url)})  # 无法识别
                        # print(Fore.BLUE + '[Unres]: Not recognized.Url: %s' % (url))
                        return False
                    if info['error'] == '4':
                        self.message.put({'error': 'Server debugging. Url: %s' % (url)})  # 服务器调试
                        # print(Fore.RED + '[Error]: Server debugging. Url: %s' % (url))
                        return False
                    if info['error'] == '5':
                        self.message.put({'error': 'Access too fast. Url: %s' % (url)})  # 访问速度太快
                        # print(Fore.RED + '[Error]: Access too fast. Url: %s' % (url))
                        return False
                except BaseException as e:
                    self.message.put({
                        'error': 'Network anomalies or Program error On: Get2Internet Destination URL:%s\n%s' % (
                            url, e)})  # 网络异常或者程序出错,抛出异常,目的域名
                    # print(Fore.RED + '[Error]: Network anomalies or Program error On: Get2Internet Destination URL:%s\n%s' % (url, e))
                    return False
            else:
                self.message.put({'info': 'More than 100 queries Url: %s' % (url)})  # 查询次数超过100次
                # print(Fore.YELLOW + '[Info]: More than 100 queries Url: %s' % (url))
                return False
        else:
            print('[Message]: Set the -i parameter')
            return False

    # 错误日志输出
    def ErrorLog(self):
        if not self.message.empty():
            while not self.message.empty():
                msg = self.message.get()
                for key, value in msg.items():
                    app.logger.error('[%s]: %s\n' % (key, value))
        print(Fore.CYAN + '[Message]: Completed generating the error log')

    # 扫描结果输出
    def ResultLog(self):
        res = []
        if not self.res.empty():
            while not self.res.empty():
                a = self.res.get()
                if a not in res:
                    res.append(a)
        print(Fore.CYAN + '[Message]: Completed generating the result log')
        return res

    def RunIt(self):
        print(Fore.CYAN + '[Message]:The program starts running...')  # 程序开始运行
        self.UrlMake2Queue()
        while not self.UrlQueue.empty():
            url = self.UrlQueue.get()
            print(url)
            print(self.whatweb)
            if not self.whatweb:
                self.CmsMake2Queue()
                corlist = [gevent.spawn(self.Get2Location, url) for i in range(self.thread)]
                gevent.joinall(corlist)
                if self.res.empty() and self.IsInternet:
                    print(
                        Fore.CYAN + '[Message]: The local fingerprint is not found, and the network interface is called.')  # 本地指纹未发现,调用网络接口
                    self.Get2Internet(url)
            else:
                self.Get2Internet(url)
        print(Fore.CYAN + '[Message]: Log generation.')  # 日志生成中
        self.ErrorLog()
        res = self.ResultLog()
        print(Fore.CYAN + '[Message]:The program end.')
        return res


# ## 命令行参数解析
# def Args():
#     parse = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, add_help=False)
#     parse.add_argument('-f', '--file', help='Please set FILE')
#     parse.add_argument('-u', '--url', help="Please set scan URL")
#     parse.add_argument('-t', '--thread', default=100, help='Please set Thread Number', type=int)
#     parse.add_argument('-w', '--whatweb', default=False, help='Use whatweb probe directly',
#                        action="store_true")  # 设置后跳过本地指纹检测,直接使用whatweb接口探测,默认为否
#     parse.add_argument('-i', '--is_internet',
#                        help="network environments,default true;if it's set,it will not be tested online", default=True,
#                        action="store_false")  # 是否可以访问互联网，默认可以，设置后表示不可以
#     args = parse.parse_args()
#     if args.url is None and args.file is None:
#         print(parse.print_help())
#         exit()
#     else:
#         return args
#
if __name__ == "__main__":
    init(autoreset=True)
    cms = CmsInfo(desurl='http://www.u-share.cn/forum.php/')
    cms.RunIt()
