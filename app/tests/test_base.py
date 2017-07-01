
from flask_testing import TestCase

from app import create_app, db
from app.models.user import User

class TestBase(TestCase):

    def create_app(self):
        config_name = 'test'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='postgresql://test:asdfasdf@localhost:5432/adoptanode_test'
        )
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
