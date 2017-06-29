

def create_order_id(context):
    order_id = "{user_id}{node_id}".format(
        user_id=context.current_parameters['user_id'],
        node_id=context.current_parameters['node_id']
    )
    return(order_id)
