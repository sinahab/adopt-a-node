
from flask import Flask, flash, redirect, render_template, request, session, abort

import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(12)

# TODO: import this from adopt_a_node.db.connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dev:asdfasdf@localhost:5432/adoptanode_development'

db = SQLAlchemy(app)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
