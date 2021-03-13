"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        user_id1 = 11
        u1.id = user_id1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        user_id2 = 22
        u2.id = user_id2

        db.session.commit()

        u1 = User.query.get(user_id1)
        u2 = User.query.get(user_id2)

        self.u1 = u1
        self.uid1 = user_id1

        self.u2 = u2
        self.uid2 = user_id2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_model(self):
        """Does basic model work?"""
    
        u = User(
            id=44,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(u.__repr__(), f'<User #{u.id}: {u.username}, {u.email}>')
        
    
    def test_is_following(self):
        """Tests is_following and is_followed_by functions."""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertFalse(self.u2.is_following(self.u1))
        self.assertTrue(self.u1.is_following(self.u2))
        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    # Testing Signup section

    def test_signup(self):
        u_signup = User.signup("test_user", "test_user@test.com", "test_password", "image.jpeg")
        test_id = 1234
        u_signup.id = test_id
        db.session.commit()

        user_test = User.query.get_or_404(test_id)
        self.assertEqual(user_test.id, 1234)
        self.assertEqual(user_test.username, "test_user")
        self.assertNotEqual(user_test.password, "test_password")
        self.assertTrue(user_test.password.startswith("$2b$12"))

    def test_signup_invalid_username(self):
        u_signup = User.signup(None, "test_user@test.com", "test_password", "image.jpeg")
        test_id = 777
        u_signup.id = test_id

        with self.assertRaises(exc.IntegrityError) as test:
            db.session.commit()

    def test_signup_invalid_email(self):
        u_signup = User.signup("TestUser", None, "test_password", "image.jpeg")
        test_id = 777
        u_signup.id = test_id

        with self.assertRaises(exc.IntegrityError) as test:
            db.session.commit()

    def test_signup_invalid_password(self):
        with self.assertRaises(ValueError) as test:
            User.signup("testtest", "email@email.com", "", "image.jpeg")

    # Testing authentication

    def test_auth(self):
        test = User.authenticate(self.u2.username, 'password')
        self.assertIsNotNone(test)

    def test_username_fail(self):
        self.assertFalse(User.authenticate("testtesttest3", "password"))

    def test_incorrect_pwd(self):
        self.assertFalse(User.authenticate(self.u2.username, "password2"))