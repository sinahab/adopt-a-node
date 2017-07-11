
from app.tests.test_base import TestBase
import datetime
from unittest.mock import patch

from app import db
from app.models.user import User
from app.models.node import Node
from app.models.invoice import Invoice

class TestInvoice(TestBase):

    def setUp(self):
        super(TestInvoice, self).setUp()

        node = Node(provider='aws', name="Bob's node")
        user = User(email='test@example.com', password='abcd')
        db.session.add(node)
        db.session.add(user)
        db.session.commit()


    @patch('app.models.invoice.BitpayClient')
    def test_generate(self, mock_bitpay_class):
        """
        Test that the BitpayClient is used to generate an invoice.
        """
        user = User.query.all()[0]
        node = Node.query.all()[0]
        invoice = Invoice(user_id=user.id, node_id=node.id, price=10.00, currency='USD')
        db.session.add(invoice)
        db.session.commit()

        mock_bitpay = mock_bitpay_class.return_value
        mock_bitpay.create_invoice_on_bitpay.return_value = True

        invoice.generate()
        mock_bitpay_class.assert_called()
        mock_bitpay.create_invoice_on_bitpay.assert_called_with(invoice)
        self.assertEqual(invoice.status, 'generated')

    @patch('app.models.invoice.BitpayClient')
    def test_generate_failure(self, mock_bitpay_class):
        """
        Test that BitpayClient's failure to create an invoice, results in the transition not completing.
        """
        user = User.query.all()[0]
        node = Node.query.all()[0]
        invoice = Invoice(user_id=user.id, node_id=node.id, price=10.00, currency='USD')
        db.session.add(invoice)
        db.session.commit()

        mock_bitpay = mock_bitpay_class.return_value
        mock_bitpay.create_invoice_on_bitpay.return_value = False

        invoice.generate()
        mock_bitpay_class.assert_called()
        mock_bitpay.create_invoice_on_bitpay.assert_called_with(invoice)
        self.assertEqual(invoice.status, 'new')

    def test_generated_minutes_ago(self):
        """
        Test the corret number of minutes are returned.
        """
        user = User.query.all()[0]
        node = Node.query.all()[0]
        invoice_created_at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
        invoice = Invoice(user_id=user.id, node_id=node.id, price=10.00, currency='USD',
            status='generated',
            bitpay_invoice_created_at=invoice_created_at
        )
        db.session.add(invoice)
        db.session.commit()

        self.assertEqual(invoice.generated_minutes_ago(), 15)

        invoice.bitpay_invoice_created_at = None
        db.session.add(invoice)
        db.session.commit()
        self.assertEqual(invoice.generated_minutes_ago(), None)

    def test_transitions_to(self):
        """
        Test that it returns all possible transitions
        """
        user = User.query.all()[0]
        node = Node.query.all()[0]
        invoice = Invoice(user_id=user.id, node_id=node.id, price=10.00, currency='USD')
        invoice.status = 'paid'
        db.session.add(invoice)
        db.session.commit()

        expected_transitions = [{ 'trigger': 'confirm', 'source': ['generated', 'paid'], 'dest': 'confirmed' }]
        self.assertEqual(invoice.possible_transitions_to('confirmed'), expected_transitions)
