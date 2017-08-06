
from datetime import datetime, timedelta

from unittest.mock import patch, PropertyMock
from .test_base import TestBase

from app import db
from app.models.user import User
from app.models.node import Node
from app.models.invoice import Invoice
from app.tasks import install_bitcoind, configure_node, delete_unprovisioned_nodes, update_node_provider_attributes

class TestTasks(TestBase):

    @patch('app.tasks.Node')
    def test_install_bitcoind(self, mock_node_class):
        """
        Test that it installs bitcoind
        """
        mock_node = mock_node_class.query.get.return_value

        install_bitcoind(123)

        mock_node.install.assert_called()

    @patch('app.tasks.Node')
    def test_configure_node_successful(self, mock_node_class):
        """
        Test that, if the node is active, it configures it.
        """
        mock_node = mock_node_class.query.get.return_value
        mock_node.provider_status = 'active'

        configure_node(123)

        mock_node.update_provider_attributes.assert_called()
        mock_node.configure.assert_called()

    @patch('app.tasks.configure_node')
    @patch('app.tasks.Node')
    def test_configure_node_unsuccessful_new(self, mock_node_class, mock_configure_node):
        """
        Test that,
        if the node is new,
        it reschedules configuration for a later time.
        """
        mock_node = mock_node_class.query.get.return_value

        mock_node.provider_status = 'new'
        configure_node(123)
        mock_node.update_provider_attributes.assert_called()
        mock_node.configure.assert_not_called()
        mock_configure_node.apply_async.assert_called()

    @patch('app.tasks.configure_node')
    @patch('app.tasks.Node')
    def test_configure_node_unsuccessful_off(self, mock_node_class, mock_configure_node):
        """
        Test that,
        if the node is off,
        it reschedules configuration for a later time.
        """
        mock_node = mock_node_class.query.get.return_value

        mock_node.provider_status = 'off'
        configure_node(123)
        mock_node.update_provider_attributes.assert_called()
        mock_node.configure.assert_not_called()
        mock_configure_node.apply_async.assert_called()

    @patch('app.tasks.configure_node')
    @patch('app.tasks.Node')
    def test_configure_node_unsuccessful_unknown(self, mock_node_class, mock_configure_node):
        """
        Test that,
        if the node has an unrecognized status,
        it throws an exception.
        """
        mock_node = mock_node_class.query.get.return_value

        mock_node.provider_status = 'exploding'
        with self.assertRaises(Exception):
            configure_node(123)
        mock_node.update_provider_attributes.assert_called()
        mock_node.configure.assert_not_called()
        mock_configure_node.apply_async.assert_not_called()

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
        node_four = Node(provider='aws', name="Node 4", status='new', created_at=twelve_day_ago)
        db.session.add(node_one)
        db.session.add(node_two)
        db.session.add(node_three)
        db.session.add(node_four)
        db.session.commit()

        invoice_one = Invoice(user_id=user.id, node_id=node_one.id, price=10.00, currency='USD', status='expired')
        invoice_two = Invoice(user_id=user.id, node_id=node_two.id, price=10.00, currency='USD', status='complete')
        invoice_three = Invoice(user_id=user.id, node_id=node_three.id, price=10.00, currency='USD', status='expired')
        db.session.add(invoice_one)
        db.session.add(invoice_two)
        db.session.add(invoice_three)
        db.session.commit()

        self.assertEqual(len(Node.query.all()), 4)
        self.assertEqual(len(Invoice.query.all()), 3)
        delete_unprovisioned_nodes()
        self.assertEqual(len(Node.query.all()), 2)
        self.assertEqual(len(Invoice.query.all()), 2)
        self.assertCountEqual(list(map(lambda n: n.name, Node.query.all())), ['Node 1', 'Node 2'])
