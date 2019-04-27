# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import pymysql
import logging
import os
import redis

basedir = os.path.abspath(os.path.dirname(__file__))

class InfoFilter(logging.Filter):
    def filter(self, record):
        """only use INFO
        筛选, 只需要 INFO 级别的log
        :param record:
        :return:
        """
        if logging.INFO <= record.levelno < logging.ERROR:
            # 已经是INFO级别了
            # 然后利用父类, 返回 1
            return super().filter(record)
        else:
            return 0


class Config:
    SECRET_KEY = 'who am i'
    DEBUG = True

    #log设置
    LOG_PATH = os.path.join(basedir, 'logs')
    LOG_PATH_ERROR = os.path.join(LOG_PATH, 'error.log')
    LOG_PATH_INFO = os.path.join(LOG_PATH, 'info.log')
    # LOG_PATH_WARNING = os.path.join(LOG_PATH, 'warning.log')
    LOG_FILE_MAX_BYTES = 100 * 1024 * 1024
    # 轮转数量是 10 个
    LOG_FILE_BACKUP_COUNT = 10
    #浏览器useragent
    HRADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'}

    @staticmethod
    def init_app(app):
        pass



class DevConfig(Config):

    #redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 14
    REDIS_USERNAME = ''
    REDIS_PASSWORD = ''

    #mysql配置
    MYSQL_HOST = '10.63.2.199'
    MYSQL_PORT = 3306
    MYSQL_DATABASE = 'host_server_win'
    MYSQL_USERNAME = 'Joynice'
    MYSQL_PASSWORD = 'liran123/'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    #指纹配置
    CMS_FINGERPRINT = os.path.join(os.getcwd(), 'fingerprint', 'cms-fingerprint')
    TEST_CMS_SITE = os.path.join(os.getcwd(), 'fingerprint', 'testwebsite')

    #用户session
    CMS_USER_ID = 'DSADSAD1551512'

    # 发送者邮箱的服务器地址
    MAIL_SERVER = "smtp.qq.com"
    MAIL_PORT = '587'
    MAIL_USE_TLS = True
    # MAIL_USE_SSL
    MAIL_USERNAME = '1125365907@qq.com'
    MAIL_PASSWORD = 'fymamdgjrovehgcd'
    MAIL_DEFAULT_SENDER = '1125365907@qq.com'

    #log设置
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import RotatingFileHandler
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(process)d %(thread)d '
            '%(pathname)s %(lineno)s %(message)s')

        # FileHandler Info
        file_handler_info = RotatingFileHandler(filename=cls.LOG_PATH_INFO)
        file_handler_info.setFormatter(formatter)
        file_handler_info.setLevel(logging.INFO)
        info_filter = InfoFilter()
        file_handler_info.addFilter(info_filter)
        app.logger.addHandler(file_handler_info)

        # FileHandler Error
        file_handler_error = RotatingFileHandler(filename=cls.LOG_PATH_ERROR)
        file_handler_error.setFormatter(formatter)
        file_handler_error.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler_error)

        # FileHandler Warning
        # file_handler_warning = RotatingFileHandler(filename=cls.LOG_PATH_WARNING)
        # file_handler_warning.setFormatter(formatter)
        # file_handler_warning.setLevel(logging.WARNING)
        # apps.logger.addHandler(file_handler_warning)


    # celery相关的配置
    CELERY_RESULT_BACKEND = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)
    CELERY_BROKER_URL = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, REDIS_DB)


config = {
    'development': DevConfig,
    'testing': None,

    'default': DevConfig
}