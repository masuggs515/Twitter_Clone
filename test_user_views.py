"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):

    def setUp(self):
        """Create test user and data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 25
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_users_list(self):
        with self.client as client:
            res = client.get('/users')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('@testuser' , html)

    
    def test_show_user(self):
        user = User.query.get_or_404(self.testuser_id)
        with self.client as client:
            res = client.get(f'/users/{user.id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<a href="/users/{ self.testuser_id }">' , html)
            

    


    