
from app.models.node import CLOUD_PROVIDERS

PROVIDERS = {
    'digital_ocean': { 'price_per_month': 10.00, 'currency': 'USD' },
    'aws': {}
}

def calculate_price(provider, number_of_months):
    """
    Calculates the total cost of spinning up a node on the provider
    for the given length of time.
    """
    if (provider not in CLOUD_PROVIDERS):
        raise("Provider {provider} is not supported.")

    price = PROVIDERS[provider]['price_per_month'] * number_of_months
    return(price)

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
