# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import json
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app
from exts import db
from models import Task
from models import Cms_fingerprint
from config import config

app = create_app()
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def add_cms_fingerprint():
    fp = open(config['development'].MANAGER_CMS_FINGERPRINT, 'rb')
    CmsData = json.load(fp, encoding="utf-8")
    for i in CmsData:
        cms = Cms_fingerprint(url=i.get('url'), re=i.get('re'), name=i.get('name'), md5=i.get('md5'))
        db.session.add(cms)
    db.session.commit()

if __name__ == '__main__':
    manager.run()