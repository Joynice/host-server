#!/usr/bin/env python
from flask import Flask
from flask_restful import Api
import config
from exts import db
from api.resource import HostServer, Result
# from flask_wtf import CSRFProtect
from apps.cms import bp as cms_bp
from apps.common import bp as common_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.config['development'])
    app.register_blueprint(cms_bp)
    app.register_blueprint(common_bp)
    config.config['development'].init_app(app)
    db.init_app(app)
    # CSRFProtect(app)
    return app


app = create_app()

api = Api(app)

api.add_resource(HostServer, '/v1/task/', endpoint='task')
api.add_resource(Result, '/v1/result/', endpoint='result')

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
