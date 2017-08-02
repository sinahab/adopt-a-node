
from flask import flash, redirect, render_template, url_for, abort, current_app
from flask_security import current_user, login_required, roles_required

from . import admin

@admin.route('/admin/', methods=['GET'])
@roles_required('admin')
@login_required
def index():
    """
    Show the admin dashboard
    """
    return render_template('admin/index.html', title="Admin")

@admin.route('/admin/users/', methods=['GET'])
@roles_required('admin')
@login_required
def users():
    """
    Show the admin users dashboard
    """
    return render_template('admin/users.html', title="Admin")
