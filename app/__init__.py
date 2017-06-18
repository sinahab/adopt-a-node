
from flask import Flask, render_template
from flask_security import Security, SQLAlchemyUserDatastore, login_required

from flask_assets import Environment
from .utils.assets import bundles

import os

from .db.models.user import User
from .db.models.role import Role
from .db.connection import db

from config import app_config

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    # assets
    assets = Environment(app)
    assets.register(bundles)

    db.init_app(app)

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Views
    @app.route('/')
    def landing():
        return render_template('landing.html')

    @app.route('/adopt/')
    @login_required
    def adopt():
        return render_template('adopt.html')

    @app.route('/nodes/')
    @login_required
    def nodes():
        return render_template('nodes.html')

    @app.route('/confirmation/')
    @login_required
    def confirmation():
        return render_template('confirmation.html')

    return app
