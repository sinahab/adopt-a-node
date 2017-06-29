

def create_order_id(context):
    """
    Creates an order_id, as a combination of the user_id and node_id.
    This is simply a visual guide for the Bitpay merchant API,
    to help us with identifying invoices.
    """
    order_id = "{user_id}{node_id}".format(
        user_id=context.current_parameters['user_id'],
        node_id=context.current_parameters['node_id']
    )
    return(order_id)
