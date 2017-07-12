
from flask import flash, redirect, render_template, url_for, abort, current_app
from flask_security import current_user, login_required

from . import node
from .forms import NewNodeForm, ExistingNodeForm
from app import db
from app.models.node import Node
from app.models.invoice import Invoice
from app.service_objects.bitpay_client import BitpayClient
from app.utils.invoice import calculate_price
from app.serializers.node_serializer import NodeSerializer

@node.route('/nodes/', methods=['GET'])
@login_required
def index():
    """
    List the user's nodes
    """
    current_user_nodes = current_user.nodes

    if current_user_nodes:
        serialized_nodes = list(map(lambda node: NodeSerializer(node), current_user_nodes))
        serialized_nodes_to_show = list(filter(lambda node: node.should_show(), serialized_nodes))
        return render_template('node/index.html', serialized_nodes=serialized_nodes_to_show, title="My Nodes")

    else:
        return render_template('node/index.html', serialized_nodes=[], title="My Nodes")

@node.route('/adopt/', methods=['GET'])
@login_required
def new():
    """
    Adopt a node: select parameters for a new node
    """
    form = NewNodeForm()
    return render_template('node/adopt.html', form=form, title="Adopt")

@node.route('/nodes/', methods=['POST'])
@login_required
def create():
    """
    Create a new node in the database
    """
    form = NewNodeForm()

    if form.validate_on_submit():

        try:
            # step 1: create a new Node record.
            node = Node(
                user=current_user,
                provider=form.provider.data,
                name=form.name.data,
                bu_ad=form.bu_ad.data,
                bu_eb=form.bu_eb.data,
                months_adopted=form.months.data
            )

            # step 2: create a new Invoice record.
            invoice = Invoice(
                user=current_user,
                node=node,
                price=calculate_price(node.provider, node.months_adopted),
                currency='USD'
            )

            # step 3: save new Node and Invoice records to the DB.
            db.session.add(node)
            db.session.add(invoice)
            db.session.commit()

            # step 4: create bitpay invoice & associate w Invoice record in DB.
            invoice.generate()

            # step 5: redirect user to bitpay url
            return redirect(invoice.bitpay_data['url'])

        except Exception as e:
            return redirect(url_for('node.new'))

    else:
        for field, errors in form.errors.items():
            flash(errors[0])

        return redirect(url_for('node.new'))

@node.route('/nodes/<int:id>', methods=['GET'])
@login_required
def edit(id):
    """
    View or edit an existing node
    """
    node = Node.query.get_or_404(id)

    if node.user != current_user:
        return redirect(url_for('node.index'))

    form = ExistingNodeForm(obj=node)
    return render_template('node/edit.html', form=form, node=node, title="Node")

@node.route('/nodes/<int:id>', methods=['POST'])
@login_required
def update(id):
    """
    Update an existing node.
    """
    node = Node.query.get_or_404(id)

    if node.user != current_user:
        return redirect(url_for('node.index'))

    form = ExistingNodeForm(obj=node)

    if form.validate_on_submit():
        node.name = form.name.data
        node.bu_eb = form.bu_eb.data
        node.bu_ad = form.bu_ad.data

        try:
            db.session.add(node)
            db.session.commit()
            flash('You have successfully edited the node.')

        except Exception as e:
            current_app.logger.error(e)

        # redirect to the nodes page
        return redirect(url_for('node.index'))

    else:
        for field, errors in form.errors.items():
            flash(errors[0])

        return redirect(url_for('node.edit', id=node.id))
