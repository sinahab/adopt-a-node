
from flask import render_template
from flask_security import login_required
from . import home

@home.route('/')
def landing():
    """
    The landing page.
    """
    return render_template('landing.html', title="Welcome")

@home.route('/confirmation/')
@login_required
def confirmation():
    """
    Confirmation page following payment of an invoice.
    """
    return render_template('confirmation.html', title="Confirmation")
