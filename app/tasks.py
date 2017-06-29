
from app import celery

from app.utils.ssh import ssh_scope

@celery.task(name="tasks.add")
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
        configure_node.apply_async((node_id), countdown=2700)

    return

from app.models.node import Node
