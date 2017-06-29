
import json
from flask import request

from . import bitpay
from app.models.invoice import Invoice
from app.service_objects.bitpay_client import BitpayClient

@bitpay.route('/bitpay', methods=['POST'])
def notification():
    """
    Uses BitpayClient to fetch new data for an invoice when a notification arrives from the Bitpay server.
    Note: it does not directly update the Invoice here, as this endpoint is open and not secure.
    Refer to Bitpay docs for guidance: https://bitpay.com/docs/invoice-callbacks
    """
    bitpay_id = request.get_json()['data']['id']
    invoice = Invoice.query.filter_by(bitpay_id=bitpay_id).first()

    if invoice:
        BitpayClient().fetch_invoice(invoice)
        return(json.dumps({'success': True}), 200, {'ContentType':'application/json'})

    else:
        return(json.dumps({'success': False}), 400, {'ContentType':'application/json'})
