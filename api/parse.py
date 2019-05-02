# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from flask_restful import reqparse

#post下发任务
HostServerPost_parse = reqparse.RequestParser()
HostServerPost_parse.add_argument('url', type=str, required=True, help='检测url')
HostServerPost_parse.add_argument('cycle', type=int, choices=(1, 3, 7), help='检测周期')
HostServerPost_parse.add_argument('number', type=int, help='检测次数')
HostServerPost_parse.add_argument('secret_key', type=str, help='身份验证')

#delete删除任务
HostServerDelete_parse = reqparse.RequestParser()
HostServerDelete_parse.add_argument('task_id', type=str, required=True, help='删除的任务ID')
HostServerDelete_parse.add_argument('secret_key', type=str,  help='身份验证')


#get 查询
HostServerGet_parse = reqparse.RequestParser()
HostServerGet_parse.add_argument('task_id', type=str, required=True, help='查询的任务ID')
HostServerGet_parse.add_argument('secret_key', type=str,  help='身份验证')

#upgrade 更新

HostServerUpgrade_parse = reqparse.RequestParser()
HostServerUpgrade_parse.add_argument('task_id', type=str, required=True, help='更新任务ID')
HostServerUpgrade_parse.add_argument('url', type=str, help='更改url')
HostServerUpgrade_parse.add_argument('cycle', type=int, help='更改周期')
HostServerUpgrade_parse.add_argument('number', type=int, help='更改次数')
HostServerUpgrade_parse.add_argument('secret_key', type=str,  help='身份验证')


#result

ResultGet_parse = reqparse.RequestParser()
ResultGet_parse.add_argument('result_id', type=str, required=True, help='查询结果ID')
ResultGet_parse.add_argument('secret_key', type=str,  help='身份验证')


