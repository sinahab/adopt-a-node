
import os
from app import create_celery

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

from app.models.node import Node
