
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_assets import Environment
from flask_migrate import Migrate
from flask_mail import Mail

import logging
from raven.handlers.logging import SentryHandler

from celery import Celery

from .utils.assets import bundles

from config import app_config

import os

db = SQLAlchemy()

def create_app(config_name):
    app = configure_app(config_name)

    # add logging
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

    # assets
    assets = Environment(app)
    assets.register(bundles)

    from .models.user import User
    from .models.role import Role

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .node import node as node_blueprint
    app.register_blueprint(node_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .bitpay import bitpay as bitpay_blueprint
    app.register_blueprint(bitpay_blueprint)

    return app

def configure_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    config_file = "{env}.py".format(env=config_name)
    app.config.from_pyfile(config_file)

    db.init_app(app)

    migrate = Migrate(app, db)

    mail = Mail(app)

    # add Sentry for error tracking
    if config_name == 'production':
        sentry_handler = SentryHandler(dsn=app.config['SENTRY_DSN'])
        sentry_handler.setLevel(logging.ERROR)
        app.logger.addHandler(sentry_handler)

    return app

# inspired by https://github.com/thrisp/flask-celery-example/blob/master/app.py
def create_celery(config_name):
    app = configure_app(config_name)
    celery = Celery('tasks', broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
