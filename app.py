
from flask import Flask, render_template
from flask_security import Security, SQLAlchemyUserDatastore, login_required

from flask_assets import Environment
from utils.assets import bundles

import os

from db.models.user import User
from db.models.role import Role
from db.connection import db, database_url

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(12)

# flask_security configurations. Docs: https://pythonhosted.org/Flask-Security/configuration.html
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = os.urandom(12)

app.config['SECURITY_CONFIRMABLE'] = False
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_RECOVERABLE'] = False # TODO: needs email setup
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_PASSWORDLESS'] = False
app.config['SECURITY_CHANGEABLE'] = False # TODO: enable this in the future, to allow changing of passwords.

app.config['SECURITY_SEND_REGISTER_EMAIL'] = False # TODO: enable this after email setup is done.

app.config['SECURITY_URL_PREFIX'] = None
app.config['SECURITY_LOGIN_URL'] = '/login'
app.config['SECURITY_LOGOUT_URL'] = '/logout'
app.config['SECURITY_REGISTER_URL'] = '/sign_up'
app.config['SECURITY_RESET_URL'] = '/reset'
app.config['SECURITY_CHANGE_URL'] = '/change'
app.config['SECURITY_CONFIRM_URL'] = '/confirm'
app.config['SECURITY_POST_LOGIN_VIEW'] = '/'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/'
app.config['SECURITY_UNAUTHORIZED_VIEW'] = '/'

app.config['SECURITY_FORGOT_PASSWORD_TEMPLATE'] = 'security/forgot_password.html'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'security/login_user.html'
app.config['SECURITY_REGISTER_USER_TEMPLATE'] = 'security/register_user.html'
app.config['SECURITY_RESET_PASSWORD_TEMPLATE'] = 'security/reset_password.html'
app.config['SECURITY_CHANGE_PASSWORD_TEMPLATE'] = 'security/change_password.html'
app.config['SECURITY_SEND_CONFIRMATION_TEMPLATE'] = 'security/send_confirmation.html'
app.config['SECURITY_SEND_LOGIN_TEMPLATE'] = 'security/send_login.html'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
