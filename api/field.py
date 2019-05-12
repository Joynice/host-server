# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from flask import jsonify


class HttpCode(object):
    ok = 200
    unautherror = 401
    paramserror = 400
    methoderror = 405
    servererror = 500


def restful_result(code, message, data):
    return jsonify({"code": code, "message": message, "data": data or {}})


def success(message="", data=None):
    print(data)
    return restful_result(code=HttpCode.ok, message=message, data=data)


def unauth_error(message=""):
    return restful_result(code=HttpCode.unautherror, message=message, data=None)


def params_error(message=""):
    return restful_result(code=HttpCode.paramserror, message=message, data=None)


def server_error(message=""):
    return restful_result(code=HttpCode.servererror, message=message or '服务器内部错误', data=None)

def method_error(message=''):
    return restful_result(code=HttpCode.methoderror, message=message, data=None)


def result_parse(cms, web, host):
    result = {}

    if cms:
        cms_result = eval(cms).get('webdna')
        cmsname = cms_result.get('cmsname')
        result.update(cms=cmsname)
    if web:
        title = eval(web).get('title')
        header = eval(web).get('header')
        body = eval(web).get('body')
        web_result = eval(web).get('other')
        if web_result:
            print(web_result)
            try:
                web_server = web_result.get('web-servers') or web_result.get('other').get('Server')
            except:
                web_server = None
            programming_languages = web_result.get('programming-languages')

            js = web_result.get('javascript-frameworks')
            web_frameworks = web_result.get('web-frameworks')
            result.update(web_server=web_server, programming_languages=programming_languages,title=title,js=js,web_frameworks=web_frameworks, header=header, body=body)
    if host:
        host_result = eval(host)
        if len(host_result)>0:
            ip = host_result[0].get('ip')
            os = host_result[0].get('os')
            port_list = []
            for i in host_result:
                port = i.get('port')
                port_list.append(port)
            result.update(ip=ip, os=os, port=port_list)

    return result

