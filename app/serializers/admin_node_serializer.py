
from dateutil.relativedelta import relativedelta

class AdminNodeSerializer():
    def __init__(self, node):
        self.node = node

    def ip_address(self):
        return(self.node.ipv4_address)

    def status(self):
        return(self.node.status)

    def name(self):
        return(self.node.name)

    def eb(self):
        eb = ("%0.2f" % self.node.bu_eb) + " MB"
        return(eb)

    def ad(self):
        return(self.node.bu_ad)

    def node_id(self):
        return(self.node.id)

    def user_email(self):
        user = self.node.user
        if user:
            return(user.email)

    def months_adopted(self):
        return(self.node.months_adopted)

    def launched_at(self):
        if self.node.launched_at:
            return(self.node.launched_at.strftime("%m-%d-%Y"))
        else:
            return('')

    def provider(self):
        if self.node.provider == 'aws':
            return('Amazon Web Services (AWS)')
        elif self.node.provider == 'digital_ocean':
            return('Digital Ocean')
        else:
            return(self.node.provider)
