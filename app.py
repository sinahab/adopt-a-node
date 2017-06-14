
from flask import Flask, render_template
from flask_security import Security, SQLAlchemyUserDatastore, login_required

import os

from db.models.user import User
from db.models.role import Role
from db.connection import db, database_url

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(12)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
# @app.before_first_request
# def create_user():
#     user_datastore.create_user(email='matt@nobien.net', password='password')
#     db.session.commit()

# Views
@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
