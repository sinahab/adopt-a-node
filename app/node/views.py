
from flask import flash, redirect, render_template, url_for
from flask_security import current_user, login_required

from . import node
from .forms import NewNodeForm, ExistingNodeForm
from app import db
from app.models.node import Node
from app.models.invoice import Invoice
from app.service_objects.bitpay_client import BitpayClient

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

        try:
            # step 1: create a new Node record in the DB.
            # TODO: calculate expiration_date
            node = Node(
                user=current_user,
                provider=form.provider.data,
                name=form.name.data,
                bu_ad=form.bu_ad.data,
                bu_eb=form.bu_eb.data
            )

            # step 2: create a new Invoice record in the DB.
            # TODO: calculate price based on time & cloud provider
            invoice = Invoice(
                user=current_user,
                node=node,
                price=4.00,
                currency='USD'
            )

            db.session.add(node)
            db.session.add(invoice)
            db.session.commit()

            # step 3: create bitpay invoice & associate w Invoice record in DB.
            invoice.generate()

            # redirect user to bitpay url
            return redirect(invoice.bitpay_data['url'])

        except Exception as e:
            return redirect(url_for('node.new'))

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
    """
    Update an existing node.
    """
    node = Node.query.get_or_404(id)
    form = ExistingNodeForm(obj=node)

    if form.validate_on_submit():
        node.name = form.name.data

        db.session.add(node)
        db.session.commit()
        flash('You have successfully edited the node.')

        # redirect to the node page
        return redirect(url_for('node.index'))
