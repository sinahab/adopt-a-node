
import os
from datetime import datetime, timedelta
from app import create_celery, db

config_name = os.getenv('FLASK_CONFIG') or 'development'
celery = create_celery(config_name)

@celery.task(name="tasks.configure_node")
def configure_node(node_id):
    """
    Checks to see whether the node has been successfully provisioned.
    If yes: it configures the node.
    If not: it schedules another check in in 45 minutes.
    """
    node = Node.query.get(node_id)

    # TODO: the if statement should check that the node has been successfully provisioned
    if True:
        node.configure()
    else:
        configure_node.apply_async((node_id), countdown=1800)

    return

@celery.task(name='tasks.delete_unprovisioned_nodes')
def delete_unprovisioned_nodes():
    """
    Deletes nodes (and their invoides) which:
    are older than 10 days,
    were never paid for and were therefore not provisioned on a cloud provider,
    and where the invoice is expired and so can never be paid for.
    """
    ten_days_ago = datetime.utcnow() - timedelta(days=10)
    nodes = Node.query.filter(Node.status=='new', Node.provider_id==None, Node.created_at <= ten_days_ago).all()

    for node in nodes:
        if node.invoice.status == 'expired':
            db.session.delete(node.invoice)
            db.session.delete(node)
            db.session.commit()

from app.models.node import Node
