
from app.tests.test_base import TestBase
from unittest.mock import patch

from app import db
from app.models.user import User
from app.models.node import Node
from app.models.invoice import Invoice

class TestInvoice(TestBase):

    @patch('app.models.invoice.BitpayClient')
    def test_generate(self, mock_bitpay_class):
        """
        Uses the BitpayClient to generate an invoice.
        """
        # setup
        node = Node(provider='aws', name="Bob's node")
        user = User(email='test@example.com', password='abcd')
        db.session.add(node)
        db.session.add(user)
        db.session.commit()

        invoice = Invoice(user_id=user.id, node_id=node.id, price=10.00, currency='USD')
        db.session.add(invoice)
        db.session.commit()

        invoice.generate()

        mock_bitpay = mock_bitpay_class.return_value
        mock_bitpay_class.assert_called()
        mock_bitpay.create_invoice_on_bitpay.assert_called_with(invoice)

    def test_generated_minutes_ago(self):
        """
        Test the corret number of minutes are returned.
        """
        # TODO:
        pass

    def test_transitions_to(self):
        """
        Test that it returns all possible transitions
        """
        # setup
        node = Node(provider='aws', name="Bob's node")
        user = User(email='test@example.com', password='abcd')
        db.session.add(node)
        db.session.add(user)
        db.session.commit()

        invoice = Invoice(user_id=user.id, node_id=node.id, price=10.00, currency='USD')
        invoice.status = 'paid'
        db.session.add(invoice)
        db.session.commit()

        expected_transitions = [{ 'trigger': 'confirm', 'source': ['generated', 'paid'], 'dest': 'confirmed' }]
        self.assertEqual(invoice.possible_transitions_to('confirmed'), expected_transitions)
