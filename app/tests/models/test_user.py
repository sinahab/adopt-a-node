
from app.tests.test_base import TestBase
from app import db

import sqlalchemy

from app.models.user import User
from app.models.role import Role

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

    def test_make_admin(self):
        """
        Test that:
        It gives the user the admin role.
        It does nothing if the user is already an admin.
        """
        user = User(email='test@example.com', password='abcd')
        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.has_role('admin'), False)
        user.make_admin()
        self.assertEqual(user.has_role('admin'), True)
        user.make_admin()
        self.assertEqual(user.has_role('admin'), True)

    def test_unmake_admin(self):
        """
        Test that:
        It removes the admin role from the user.
        It does nothing if the user is not an admin already.
        """
        user = User(email='test@example.com', password='abcd')
        role = Role.query.filter_by(name='admin').all()[0]
        user.roles.append(role)
        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.has_role('admin'), True)
        user.unmake_admin()
        self.assertEqual(user.has_role('admin'), False)
        user.unmake_admin()
        self.assertEqual(user.has_role('admin'), False)
