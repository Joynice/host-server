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

def result_parse(cms, web):
    result = {}
    try:
        if cms:
            cms_result = eval(cms).get('webdna')
            result.update(cms=cms_result)
        if web:
            web_result = eval(web).get('other')
            result.update(web=web_result)
    except:
        pass
    return result

