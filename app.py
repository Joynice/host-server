#!/usr/bin/env python
from flask import Flask
from flask_restful import Api
import config
from exts import db, socketio
from api.resource import HostServer, Result
# from  flask_wtf import CsrfProtect
from apps.cms import bp as cms_bp
from apps.front import bp as front_bp
import datetime
from apps.common import bp as common_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.config['development'])
    app.register_blueprint(cms_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(front_bp)
    config.config['development'].init_app(app)
    db.init_app(app)
    app.permanent_session_lifetime = datetime.timedelta(seconds=60 * 60 * 6) #设置session时间
    socketio.init_app(app)
    # CsrfProtect(app)
    return app


app = create_app()

api = Api(app)

api.add_resource(HostServer, '/v1/task/', endpoint='task')
api.add_resource(Result, '/v1/result/', endpoint='result')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
