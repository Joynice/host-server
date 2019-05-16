# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import os
import re
import subprocess
from xml.dom import minidom

from host_scan_task import host_celery_app
from scan.dosql import Mysql
from utils.web_tools import urlTosite


class Nmap(object):
    def __init__(self, url):
        self.url = url
        self.domain = urlTosite(url)
        self.mysql = Mysql()

    def scan(self, taskid):
        path = 'D:\\events\\host-server\\scan\\hostscan\\tools\\nmap\\nmap.exe'
        print(path)
        self.resultpath = 'D:\\events\\host-server\\scan\\hostscan\\tools\\result\\{}.xml'.format(taskid)
        if os.path.exists(path):
            print(self.domain)
            cmd = "%s %s -Pn -sV -O --osscan-guess -oX %s" % (path, self.domain, self.resultpath)
            print(cmd)
            a = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            result = a.communicate()[0]
            try:
                self.os = re.findall('\\r\\nService Info: (.*?)\\r\\n\\r\\nOS', str(result, encoding='gbk'), re.I)[0]
            except:
                self.os = ''

    def parse(self):
        try:
            open_ports = []
            document_tree = minidom.parse(self.resultpath)
            ip = document_tree.getElementsByTagName('address')[0].getAttribute('addr') or ''
            print(ip)
            ports = document_tree.getElementsByTagName('port')
            if self.os=='':
                os_purpose = document_tree.getElementsByTagName('osmatch')[0].getAttribute('name') or ''
                self.os = os_purpose
            for port in ports:
                port_dict = {}
                data_dict = {}
                data_dict.update(ip=ip, os=self.os)
                protocol = port.getAttribute('protocol') or None
                portid = port.getAttribute('portid') or None
                state = port.childNodes[0].getAttribute('state') or ''
                service_name = port.childNodes[1].getAttribute('name') or ''
                product = port.childNodes[1].getAttribute('product') or ''
                version = port.childNodes[1].getAttribute('version') or ''
                extrainfo = port.childNodes[1].getAttribute('extrainfo') or ''
                tunnel = port.childNodes[1].getAttribute('tunnel') or ''
                Service = '{}/{}'.format(tunnel, service_name) if tunnel else service_name
                Version = product + ' ' + version + ' ' + '({})'.format(extrainfo) if extrainfo else product + ' ' + version
                port_dict.update(protocol=protocol, portid=portid, state=state, service=Service, version=Version)
                data_dict.update(port=port_dict)
                open_ports.append(data_dict)
            os.remove(self.resultpath)
        except Exception as e:
            print(e)
            open_ports = []
            os.remove(self.resultpath)
        return open_ports

    def run(self, taskid):
        self.scan(taskid=taskid)
        result = self.parse()
        # status = self.mysql.query(table='task', obj='state', factor='task_id="dz2UN5WxjwNBABGnmAm9nk"', num='one')
        self.mysql.sql("UPDATE `task` SET `host_result`=\"{}\" WHERE `task_id`='{}'".format(str(result), taskid))


@host_celery_app.task
def host_scan(url, taskid):
    nmap = Nmap(url=url)
    nmap.run(taskid=taskid)


if __name__ == '__main__':
    nmap = Nmap(url='http://szjy.xxu.edu.cn/').run(taskid='uxNPjki6QzMJTcbcVJKv2n')