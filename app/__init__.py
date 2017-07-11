
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_assets import Environment
from flask_migrate import Migrate
import logging

from celery import Celery

from .utils.assets import bundles

from config import app_config

import os

db = SQLAlchemy()

def create_app(config_name):
    app = configure_app_with_db(config_name)

    # add logging
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

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

    from .bitpay import bitpay as bitpay_blueprint
    app.register_blueprint(bitpay_blueprint)

    return app

def configure_app_with_db(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    config_file = "{env}.py".format(env=config_name)
    app.config.from_pyfile(config_file)

    db.init_app(app)

    migrate = Migrate(app, db)

    return app

# inspired by https://github.com/thrisp/flask-celery-example/blob/master/app.py
def create_celery(config_name):
    app = configure_app_with_db(config_name)
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
