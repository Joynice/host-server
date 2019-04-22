from flask import Flask
from flask_restful import Api
import config
from exts import db
from api.resource import HostServer, Result

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.config['development'])
    config.config['development'].init_app(app)
    db.init_app(app)
    return app

app = create_app()

api = Api(app)

api.add_resource(HostServer, '/v1/task/', endpoint='task')
api.add_resource(Result, '/v1/result/', endpoint='result')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
