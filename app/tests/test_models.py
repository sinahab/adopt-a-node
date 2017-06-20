
from .test_base import TestBase
from app import db

import sqlalchemy

from app.models.user import User
from app.models.node import Node

class TestModels(TestBase):

    def test_user(self):
        """
        Test the creation of User records
        """
        user_one = User(email='test_one@example.com', password='abcd')
        user_two = User(email='test_two@example.com', password='abcd')

        db.session.add(user_one)
        db.session.add(user_two)
        db.session.commit()

        self.assertEqual(User.query.count(), 2)

    def test_user_email_uniqueness(self):
        """
        Test that users are required to have unique emails
        """

        user_one = User(email='test@example.com', password='abcd')
        user_two = User(email='test@example.com', password='abcd')

        db.session.add(user_one)
        db.session.commit()

        db.session.add(user_two)

        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.commit()

    def test_node(self):
        """
        Test the creation of Node records
        """
        node_one = Node(provider='aws', name="Bob's node")
        node_two = Node(provider='digital_ocean', name="Bob's node")

        db.session.add(node_one)
        db.session.add(node_two)
        db.session.commit()

        self.assertEqual(Node.query.count(), 2)

    def test_node_provider_allowed(self):
        """
        Test that a Node's provider field must be included in 'aws' or 'digital_ocean'
        """
        with self.assertRaises(AssertionError):
            node = Node(provider='linode', name="Bob's node")
