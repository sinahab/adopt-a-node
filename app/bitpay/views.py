
import json
from flask import request

from . import bitpay

@bitpay.route('/bitpay', methods=['POST'])
def notification():
    """
    Receives notifications from the Bitpay invoice server.
    """
    print("JSON")
    print(request.get_json())

    print("DATA")
    print(request.values)

    return(json.dumps({'success':True}), 200, {'ContentType':'application/json'})
