
from datetime import datetime, timedelta

from .test_base import TestBase

from app import db
from app.models.user import User
from app.models.node import Node
from app.models.invoice import Invoice
from app.tasks import delete_unprovisioned_nodes

class TestTasks(TestBase):

    def test_delete_unprovisioned_nodes(self):
        """
        Test that
        old nodes that were never provisioned are deleted,
        along with their invoices.
        """
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        twelve_day_ago = datetime.utcnow() - timedelta(days=12)

        user = User(email='test@example.com', password='abcd')
        db.session.add(user)
        db.session.commit()

        node_one = Node(provider='aws', name="Node 1", status='new', created_at=one_day_ago)
        node_two = Node(provider='aws', name="Node 2", status='up', created_at=twelve_day_ago)
        node_three = Node(provider='aws', name="Node 3", status='new', created_at=twelve_day_ago)
        db.session.add(node_one)
        db.session.add(node_two)
        db.session.add(node_three)
        db.session.commit()

        invoice_one = Invoice(user_id=user.id, node_id=node_one.id, price=10.00, currency='USD', status='expired')
        invoice_two = Invoice(user_id=user.id, node_id=node_two.id, price=10.00, currency='USD', status='complete')
        invoice_three = Invoice(user_id=user.id, node_id=node_three.id, price=10.00, currency='USD', status='expired')
        db.session.add(invoice_one)
        db.session.add(invoice_two)
        db.session.add(invoice_three)
        db.session.commit()

        self.assertEqual(len(Node.query.all()), 3)
        self.assertEqual(len(Invoice.query.all()), 3)
        delete_unprovisioned_nodes()
        self.assertEqual(len(Node.query.all()), 2)
        self.assertEqual(len(Invoice.query.all()), 2)
        self.assertCountEqual(list(map(lambda n: n.name, Node.query.all())), ['Node 1', 'Node 2'])
