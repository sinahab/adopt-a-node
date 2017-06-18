
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_assets import Environment
from flask_migrate import Migrate

from .utils.assets import bundles

from config import app_config

import os

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    # assets
    assets = Environment(app)
    assets.register(bundles)

    db.init_app(app)

    migrate = Migrate(app, db)

    from .models.user import User
    from .models.role import Role

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # TODO: fill in the admin views.
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    return app
