
from flask import flash, redirect, render_template, url_for
from flask_security import current_user, login_required

from . import node
from .forms import NewNodeForm, ExistingNodeForm
from .. import db
from ..models.node import Node

@node.route('/nodes/', methods=['GET'])
@login_required
def index():
    """
    List the user's nodes
    """
    nodes = current_user.nodes

    return render_template('node/index.html', nodes=nodes, title="My Nodes")

@node.route('/adopt/', methods=['GET'])
@login_required
def new():
    """
    Adopt a node: select parameters for a new node
    """
    form = NewNodeForm()
    return render_template('node/adopt.html', form=form, title="Adopt a Node")

@node.route('/nodes/', methods=['POST'])
@login_required
def create():
    """
    Create a new node in the database
    """
    form = NewNodeForm()

    if form.validate_on_submit():
        node = Node(
            user=current_user,
            provider=form.provider.data,
            name=form.name.data
        )

        try:
            # add node to the database
            db.session.add(node)
            db.session.commit()
            flash('You have successfully added a new node.')

        except Exception as e:
            flash(str(e))

        # redirect to nodes page
        return redirect(url_for('node.index'))

@node.route('/nodes/<int:id>', methods=['GET'])
@login_required
def edit(id):
    """
    View or edit an existing node
    """
    node = Node.query.get_or_404(id)
    form = ExistingNodeForm(obj=node)
    return render_template('node/edit.html', form=form, node=node, title="Node")

@node.route('/nodes/<int:id>', methods=['POST'])
@login_required
def update(id):
    node = Node.query.get_or_404(id)
    form = ExistingNodeForm(obj=node)

    if form.validate_on_submit():
        node.name = form.name.data

        db.session.add(node)
        db.session.commit()
        flash('You have successfully edited the node.')

        # redirect to the node page
        return redirect(url_for('node.index'))
