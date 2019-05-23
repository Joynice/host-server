# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import re

from flask import Blueprint, views, render_template, request
from sqlalchemy import func

from api import field
from models import Asset
from utils.web_tools import match_url, urlTodomain

bp = Blueprint('front', __name__)


class IndexView(views.MethodView):

    def get(self):
        return render_template('front/index.html')

    def post(self):
        result_list = []
        search = request.form.get('search')
        print(search)
        if search:
            if match_url(search):
                asert = Asset.query.filter(Asset.url.contains(urlTodomain(search))).all()
            elif search.lower().startswith('title='):
                context = re.search(r"title=\"(.*?)\"", search, re.I).groups()[0]
                asert = Asset.query.filter(Asset.title.contains(context)).order_by(Asset.upgrade_time).all()
            elif search.lower().startswith('server='):
                context = re.search(r"server=\"(.*?)\"", search, re.I).groups()[0]
                asert = Asset.query.filter(func.lower(Asset.web_servers).contains(func.lower(context))).order_by(Asset.upgrade_time).all()
            elif search.lower().startswith('os'):
                context = re.search(r"os=\"(.*?)\"", search, re.I).groups()[0]
                asert = Asset.query.filter(func.lower(Asset.operating_systems).contains(func.lower(context))).order_by(Asset.upgrade_time).all()
            elif search.lower().startswith('ip'):
                context = re.search(r"ip=\"(.*?)\"", search, re.I).groups()[0]
                asert = Asset.query.filter_by(ip=context).order_by(Asset.upgrade_time).all()
            else:
                return field.params_error(message='不支持查询类型！')
            if asert:
                for i in asert:
                    result = {'url': '', 'ip': '', 'web_server': '', 'jsf': '', 'pj': '', 'wf': '', 'os': '',
                              'cms': '',
                              'title': '', 'ports': '', 'ut': ''}
                    result['url'] = i.url
                    result['ip'] = i.ip
                    result['web_server'] = i.web_servers
                    result['jsf'] = i.javascript_frameworks
                    result['pj'] = i.programming_languages
                    result['wf'] = i.web_frameworks
                    result['os'] = i.operating_systems
                    result['cms'] = i.cms
                    result['title'] = i.title
                    result['ports'] = i.ports
                    result['ut'] = str(i.upgrade_time)
                    result_list.append(result)
                return field.success(data=result_list, message='查询成功!')
            else:
                return field.params_error(message='没有查到相关信息！')


bp.add_url_rule('/', view_func=IndexView.as_view('index'))
