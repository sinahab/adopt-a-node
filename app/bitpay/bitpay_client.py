
from flask import current_app
from bitpay.client import Client


# TODO: change transactionSpeed to 'low'
# TODO: fill in real customer email
# TODO: posData: Order reference number from the point-of-sale (POS). It should be a unique identifer for each order that you submit. Field is a passthru-variable returned in the payment notification post, without any modifications, for you to match up the BitPay payment notification with the request that was sent to BitPay.

class BitpayClient():
    def __init__(self):
        with open(current_app.config['BITPAY_PEM_FILE'], 'r') as pem_file:
            pem = pem_file.read().rstrip().replace('\\n', '\n')

        tokens = current_app.config['BITPAY_TOKEN']
        self.client = Client(api_uri="https://test.bitpay.com", pem=pem, tokens=tokens)

    def create_invoice(self, price):
        params = {
            'token': self.client.tokens['merchant'],
            'price': price,
            'currency': 'USD',
            'itemDesc': 'Adopt-a-Node',
            'redirectURL': "{base_uri}/confirmation".format(base_uri=current_app.config['APP_BASE_URI']),
            'notificationURL': "{base_public_uri}/bitpay".format(base_public_uri=current_app.config['APP_BASE_PUBLIC_URI']),
            'posData': '1',
            'transactionSpeed': 'high',
            'extendedNotifications': True,
            'buyer': {
                'email': 'sinahab@gmail.com',
                'notify': True
            }
        }
        invoice = self.client.create_invoice(params)
        return(invoice)
