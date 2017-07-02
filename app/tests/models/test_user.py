
from app.tests.test_base import TestBase
from app import db

import sqlalchemy

from app.models.user import User

class TestUser(TestBase):

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
