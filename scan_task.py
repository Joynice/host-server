# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from celery import Celery

celery_app = Celery('app',include=['webscan.scan.cmstest'])
celery_app.config_from_object('celery_config')