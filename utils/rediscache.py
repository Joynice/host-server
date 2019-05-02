# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import redis

from config import config

host = config['development'].REDIS_HOST
port = config['development'].REDIS_PORT
db = config['development'].REDIS_MONITOR_DB
r = redis.Redis(host=host, port=port, db=db, decode_responses=True)


def set(key, value):
    return r.set(key, value)


def get(key):
    return r.get(key)


def get_key():
    return r.keys()
