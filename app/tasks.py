
import os
from datetime import datetime, timedelta
import pytz
from celery.schedules import crontab
from app import create_celery, db

config_name = os.getenv('FLASK_CONFIG') or 'development'
celery = create_celery(config_name)

@celery.task(name="tasks.install_bitcoind")
def install_bitcoind(node_id):
    """
    It installs bitcoind on the node.
    """
    node = Node.query.get(node_id)
    node.install()
    return

@celery.task(name="tasks.configure_node")
def configure_node(node_id):
    """
    Checks to see whether the node has been successfully provisioned.
    If yes: it configures the node.
    If not: it schedules another check in in 45 minutes.
    """
    node = Node.query.get(node_id)

    node.update_provider_attributes()

    if node.provider_status == 'active':
        node.configure()
    elif node.provider_status in ['new', 'off']:
        configure_node.apply_async((node_id), countdown=1800)
    else:
        raise Exception('Error: celery configuration task failed because provider_status is not understood.')

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
        if not node.invoice:
            db.session.delete(node)
            db.session.commit()
        elif node.invoice.status == 'expired':
            db.session.delete(node.invoice)
            db.session.delete(node)
            db.session.commit()

@celery.task(name='tasks.expire_nodes')
def expire_nodes():
    """
    Expire nodes which have expired.
    """
    nodes = Node.query.filter_by(status='up').all()
    nodes = list(filter(lambda n: n.has_expired(), nodes))

    for node in nodes:
        node.expire()

@celery.task(name='tasks.update_node_provider_attributes')
def update_node_provider_attributes():
    """
    Updates provider attributes for all nodes.
    """
    nodes = Node.query.filter(
        (Node.status=='up') |
        (Node.status=='on') |
        (Node.status=='off') |
        (Node.status=='taking_snapshot') |
        (Node.status=='updating_client')
    ).all()

    for node in nodes:
        node.update_provider_attributes()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every Thursdays at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=4),
        delete_unprovisioned_nodes()
    )

    # Executes every day at 1:10am
    sender.add_periodic_task(
        crontab(hour=1, minute=10),
        update_node_provider_attributes()
    )

    # Executes every day at 1:30am
    sender.add_periodic_task(
        crontab(hour=1, minute=30),
        expire_nodes()
    )

from app.models.node import Node
