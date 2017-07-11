
from dateutil.relativedelta import relativedelta

class NodeSerializer():
    def __init__(self, node):
        self.node = node

    def info(self):
        if self.node.status == 'new' and self.node.invoice.status == 'generated' and self.node.invoice.generated_minutes_ago() and self.node.invoice.generated_minutes_ago() < 30:
            return({'message': 'Pending payment', 'link': self.node.invoice.bitpay_data['url'] })
        elif self.node.status == 'new' and self.node.invoice.status in ('paid', 'confirmed'):
            return({'message': 'Pending block confirmations', 'link': None })
        elif self.node.status in ('provisioned', 'configured'):
            return({'message': 'Provisioning', 'link': None })
        elif self.node.status == 'up':
            return({'message': self.node.ipv4_address, 'link': "https://bitnodes.21.co/nodes/{ip}-8333/".format(ip=self.node.ipv4_address)})
        elif self.node.status == 'updating_client':
            return({'message': 'Upgrading client', 'link': None })
        elif self.node.status == 'taking_snapshot':
            return({'message': 'Taking snapshot', 'link': None })
        else:
            return({'message': '...', 'link': None })

    def should_show(self):
        if self.node.status == 'new' and self.node.invoice.status not in ('generated', 'paid', 'confirmed', 'complete'):
            return(False)

        return(True)

    def should_show_details_button(self):
        if self.node.status == 'new':
            return(False)

        return(True)

    def name(self):
        return(self.node.name)

    def eb(self):
        eb = ("%0.2f" % self.node.bu_eb) + " MB"
        return(eb)

    def ad(self):
        return(self.node.bu_ad)

    def node_id(self):
        return(self.node.id)

    def launched_at(self):
        if self.node.launched_at:
            return(self.node.launched_at.strftime("%m-%d-%Y"))
        else:
            return('')

    def expires_at(self):
        if self.node.launched_at:
            expires_at = self.node.launched_at + relativedelta(months=self.node.months_adopted)
            return(expires_at.strftime("%m-%d-%Y"))
        else:
            return('')

    def provider(self):
        if self.node.provider == 'aws':
            return('Amazon Web Services (AWS)')
        elif self.node.provider == 'digital_ocean':
            return('Digital Ocean')
        else:
            return(self.node.provider)
