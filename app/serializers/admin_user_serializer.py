
class AdminUserSerializer():
    def __init__(self, user):
        self.user = user

    def email(self):
        return(self.user.email)

    def is_admin(self):
        return(self.user.has_role('admin'))

    def created_at(self):
        return(self.user.created_at.strftime("%m-%d-%Y"))

    def count_nodes(self):
        return(len(self.user.nodes))
