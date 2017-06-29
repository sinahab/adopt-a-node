
from datetime import datetime
from flask import current_app

from app import db
from bitpay.client import Client

class BitpayClient():
    def __init__(self):
        with open(current_app.config['BITPAY_PEM_FILE'], 'r') as pem_file:
            pem = pem_file.read().rstrip().replace('\\n', '\n')
        tokens = current_app.config['BITPAY_TOKEN']
        self.client = Client(api_uri="https://test.bitpay.com", pem=pem, tokens=tokens)

    def create_invoice_on_bitpay(self, invoice):
        """
        Creates an invoice on Bitpay in accordance with the provided Invoice db record
        """
        params = {
            'token': self.client.tokens['merchant'],
            'price': invoice.price,
            'currency': invoice.currency,
            'itemDesc': 'Adopt-a-Node',
            'redirectURL': "{base_uri}/confirmation".format(base_uri=current_app.config['APP_BASE_URI']),
            'notificationURL': "{base_public_uri}/bitpay".format(base_public_uri=current_app.config['APP_BASE_PUBLIC_URI']),
            'orderId': invoice.order_id, # this id makes it easier to track orders in the Bitpay merchant UI.
            'posData': invoice.id, # this is a unique identifier that will be sent back by Bitpay with notifications.
            'transactionSpeed': 'low',
            'extendedNotifications': True,
            'buyer': {
                'email': invoice.user.email,
                'notify': True
            }
        }

        bitpay_invoice = self.client.create_invoice(params)

        invoice.bitpay_invoice_created_at = datetime.utcfromtimestamp(bitpay_invoice['invoiceTime']/1000)
        invoice.bitpay_id = bitpay_invoice['id']
        del bitpay_invoice['token']
        invoice.bitpay_data = bitpay_invoice

        try:
            db.session.add(invoice)
            db.session.commit()

        except Exception as e:
            print(e)

        return(invoice)
