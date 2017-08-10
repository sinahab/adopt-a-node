
from app.tests.test_base import TestBase
from unittest.mock import patch, MagicMock

from app import db
from app.models.user import User
from app.models.node import Node
from app.models.invoice import Invoice
from app.service_objects.bitpay_client import BitpayClient


class TestBitpayClient(TestBase):

    @patch('app.models.node.install_bitcoind')
    @patch('app.models.node.AWSNodeManager')
    @patch('app.service_objects.bitpay_client.Client')
    def test_fetch_invoice(self, mock_bitpay_client_class, mock_aws_manager_class, mock_install_task):
        """
        Test that the invoice can make the required transition.
        """
        # setup
        node = Node(provider='aws', name="Bob's node")
        user = User(email='test@example.com', password='abcd')
        db.session.add(node)
        db.session.add(user)
        db.session.commit()
        invoice = Invoice(user_id=user.id, node_id=node.id, price=10.00, currency='USD', bitpay_id='123asdf', status='paid')
        db.session.add(invoice)
        db.session.commit()

        mock_bitpay_client = mock_bitpay_client_class.return_value
        mock_bitpay_client.get_invoice.return_value = {
            'posData': invoice.id,
            'status': 'confirmed',
            'btcPrice': '0.002991',
            'price': 10,
            'invoiceTime': 1502322717554,
            'expirationTime': 1502323617554,
            'currentTime': 1502326540029,
            'id': '123asdf',
            'token': 'asdfasdfasdf'
        }

        self.assertEqual(invoice.bitpay_invoice_created_at, None)
        BitpayClient().fetch_invoice(invoice)

        mock_bitpay_client.get_invoice.assert_called_with('123asdf')
        db.session.refresh(invoice)
        self.assertEqual(invoice.status, 'confirmed')
        self.assertNotEqual(invoice.bitpay_invoice_created_at, None)
