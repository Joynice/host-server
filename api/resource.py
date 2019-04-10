# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from flask_restful import Resource
from models import Task, Asset
from . import field
from .parse import HostServerPost_parse, HostServerDelete_parse, HostServerGet_parse, HostServerUpgrade_parse, \
    ResultGet_parse
from exts import db


class HostServer(Resource):

    def get(self):
        '''
        根据Task_id获取任务信息
        :return:
        '''
        args = HostServerGet_parse.parse_args()
        task_id = args.get('task_id')
        if not task_id:
            return field.params_error(message='参数缺失')
        task = Task.query.filter_by(task_id=task_id).first()
        if task:
            return field.success(message='获取状态成功！',
                                 data={'task_id': task_id, 'url': task.url, 'cycle': task.cycle, 'number': task.number,
                                       'state': task.state, 'result_id': task.result_id})

    def post(self):
        '''
        下发任务
        :return:
        '''
        from WebServer import Cms
        args = HostServerPost_parse.parse_args()
        url = args.get('url')
        cycle = args.get('cycle')
        number = args.get('number')
        if url and cycle and number:
            task = Task(url=url, cycle=str(cycle), number=number)
            db.session.add(task)
            try:
                db.session.commit()
            except Exception as e:
                return field.params_error(message=e)
            task_id = task.task_id
            result_id = task.result_id
            if number == 1:
                Cms.WebCms(desurl=url).RunIt()
            return field.success(message='下发成功', data={'task_id': task_id, 'result_id': result_id})
        else:
            return field.params_error(message='参数缺失')

    def put(self):
        '''
        更新任务
        :return:
        '''
        args = HostServerUpgrade_parse.parse_args()
        task_id = args.get('task_id')
        url = args.get('url')
        cycle = args.get('cycle')
        number = args.get('number')
        if not task_id:
            return field.params_error(message='请传入更新ID')
        if url or cycle or number:
            task = Task.query.filter_by(task_id=task_id).first()
            if task:
                task.url = url or task.url
                task.number = number or task.number
                task.cycle = cycle or task.cycle
                db.session.commit()
            else:
                return field.params_error(message='没有找到该任务')
        else:
            return field.params_error(message='参数缺失')

    def delete(self):
        '''
        删除任务
        :return:
        '''
        args = HostServerDelete_parse.parse_args()
        task_id = args.get('task_id')
        if not task_id:
            return field.params_error(message='参数缺少')
        task = Task.query.filter_by(task_id=task_id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            return field.success(message='删除任务成功')
        else:
            return field.params_error(message='没有查到任务')


class Result(Resource):
    '''
    获取结果
    '''

    def get(self):
        args = ResultGet_parse.parse_args()
        result_id = args.get('result_id')
        if not result_id:
            return field.params_error('参数缺失')
        result1 = Task.query.filter_by(result_id=result_id).first()
        if result1:
            result_data = result1.result
            return field.success(message='查询成功',
                                 data={'task_id': result1.task_id, 'result_id': result_id, 'result': result_data})

    def post(self):
        return field.method_error(message='不接受方法请求')
