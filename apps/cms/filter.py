# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

def StringToInt(Str):
    if Str == 'Cycle.ONEDAY':
        return 1
    elif Str == 'Cycle.THREEDAY':
        return 3
    elif Str == 'Cycle.WEEK':
        return 7
    elif Str == 'Cycle.HALF_MONTH':
        return 15
    elif Str == 'Cycle.ONEMONTH':
        return 30
    elif Str == 'State.WAIT_SCAN':
        return '等待扫描'
    elif Str == 'State.ING_SCAN':
        return '正在扫描'
    elif Str == 'State.FINISH_SCAN':
        return '完成扫描'

def IntToString(Int):
    if Int == 1:
        return 'Cycle.ONEDAY'
    elif Int == 3:
        return 'Cycle.THREEDAY'
    elif Int == 7:
        return 'Cycle.WEEK'
    elif Int == 15:
        return 'Cycle.HALF_MONTH'
    elif Int == 30:
        return 'Cycle.ONEMONTH'


def IntToStatus(Int):
    if Int == 1:
        return 'LoginEnum.UP'
    else:
        return 'LoginEnum.DOWN'

def StatusToString(status):
    if status == 'LoginEnum.UP':
        return '在线'
    else:
        return '离线'

def NoneToString(none):
    if none == 'None':
        return '未启用'
    else:
        pass

def NoneToNone(none):
    if none == 'None' or none==None:
        return ''
    else:
        return none

def TitleToShort(title):
    if title:
        if len(title)>=30:
            return title[0:30] + '......'
        else:
            return title
    return ''


