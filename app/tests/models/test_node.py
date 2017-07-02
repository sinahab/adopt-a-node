
from app.tests.test_base import TestBase
from app import db

import sqlalchemy

from app.models.node import Node

class TestNode(TestBase):
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
