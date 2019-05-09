# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from celery import Celery

web_celery_app = Celery('app',include=['scan.webscan.Cms'])
web_celery_app.config_from_object('web_celery_config')

