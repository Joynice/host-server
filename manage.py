# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import json

import requests
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app
from config import config
from exts import db
from models import Cms_fingerprint, TestWebsite

app = create_app()
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


# 将本地指纹库上传数据库
@manager.command
def add_cms_fingerprint():
    fp = open(config['development'].CMS_FINGERPRINT, 'rb')
    CmsData = json.load(fp, encoding="utf-8")
    for i in CmsData:
        cms = Cms_fingerprint(url=i.get('url'), re=i.get('re'), name=i.get('name'), md5=i.get('md5'))
        db.session.add(cms)
    db.session.commit()

@manager.command
def add_test_cms():
    fp = open(config['development'].TEST_CMS_SITE, 'rb')
    TestData = json.load(fp, encoding="utf-8")
    for i in TestData:
        try:
            req = requests.get(i.get('manufacturerUrl'), headers = config['development'].HRADER)
            if req.status_code == 200:
                if i.get('recognitionType_id') == 1:
                    print(i)
                    cms = TestWebsite(manufacturerUrl=i.get('manufacturerUrl'), manufacturerName=i.get('manufacturerName'),
                                      name=i.get('program_name'), url=i.get('url'), md5=i.get('recognition_content'))
                else:
                    print(22222222222222222222222222222222222)
                    cms = TestWebsite(manufacturerUrl=i.get('manufacturerUrl'), manufacturerName=i.get('manufacturerName'),
                                      name=i.get('program_name'), url=i.get('url'), re=i.get('recognition_content'))
                db.session.add(cms)
                db.session.commit()
        except:
            pass


if __name__ == '__main__':
    manager.run()