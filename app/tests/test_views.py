
from flask import url_for

from .test_base import TestBase

class TestViews(TestBase):

    def test_homepage_view(self):
        """
        Test that landing page is accessible without login
        """
        response = self.client.get(url_for('home.landing'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        """
        Test that login page is accessible without login
        """
        response = self.client.get(url_for('security.login'))
        self.assertEqual(response.status_code, 200)

    def test_nodes_index_view(self):
        """
        Test that the node.index page is not accessible without login
        and redirects to login page then to index
        """
        target_url = url_for('node.index')
        redirect_url = url_for('security.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_nodes_new_view(self):
        """
        Test that the node.new page is not accessible without login
        and redirects to login page then to node.new page
        """
        target_url = url_for('node.new')
        redirect_url = url_for('security.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)
