
from flask import render_template
from flask_security import login_required

from . import user

@user.route('/')
def landing():
    return render_template('user/landing.html', title="Welcome")

@user.route('/adopt/')
@login_required
def adopt():
    return render_template('user/adopt.html', title="Adopt")

@user.route('/nodes/')
@login_required
def nodes():
    return render_template('user/nodes.html', title="My Nodes")

@user.route('/confirmation/')
@login_required
def confirmation():
    return render_template('user/confirmation.html', title="Confirmation")
