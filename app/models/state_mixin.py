
# Inspired by: https://github.com/pytransitions/transitions/issues/141

from sqlalchemy.ext.declarative import declared_attr
from transitions import Machine

from app import db

class StateMixin(object):
    @declared_attr
    def __tablename__(cls):
        return(cls.__name__.lower())

    @property
    def state(self):
        return(self.status)

    @state.setter
    def state(self, value):
        if self.status != value:
            self.status = value

    def after_state_change(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def init_state_machine(cls, obj, *args, **kwargs):
        machine = Machine(model=obj, states=cls.states, transitions=cls.transitions, initial=obj.status,
                          after_state_change='after_state_change')

        # in case that we need to have machine obj in model obj
        setattr(obj, 'machine', machine)
