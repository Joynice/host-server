# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from celery import Celery

host_celery_app = Celery('app',include=['scan.hostscan.PortScan'])
host_celery_app.config_from_object('host_celery_config')