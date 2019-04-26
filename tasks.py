# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from celery import Celery
from apps import create_app
from WebServer.Cms import WebCms
app = create_app()


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@celery.task
def cms(url):
    WebCms(desurl=url).RunIt()
