
from flask import flash, redirect, render_template, url_for, abort, current_app
from flask_security import current_user, login_required, roles_required

from . import admin

from app.models.user import User
from app.models.node import Node
from app.serializers.admin_node_serializer import AdminNodeSerializer

NODES_PER_PAGE = 10

@admin.route('/admin/', methods=['GET'])
@roles_required('admin')
@login_required
def index():
    """
    Show the admin dashboard
    """
    node_count = len(Node.query.filter_by(status='up').all())
    user_count = len(User.query.all())
    counts = {
        'user_count': user_count,
        'node_count': node_count
    }

    return render_template('admin/index.html', title="Admin", counts=counts)

@admin.route('/admin/users/', methods=['GET'])
@roles_required('admin')
@login_required
def users():
    """
    Show the admin users dashboard
    """
    return render_template('admin/users.html', title="Admin -> Users")

@admin.route('/admin/nodes/<int:page>', methods=['GET'])
@roles_required('admin')
@login_required
def nodes(page=1):
    """
    Show the admin nodes dashboard
    """
    nodes = Node.query.paginate(page, NODES_PER_PAGE, False)
    return render_template('admin/nodes.html', nodes=nodes, title="Admin -> Nodes")
