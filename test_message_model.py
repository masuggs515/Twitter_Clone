"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import Likes, db, User, Message, Follows
from sqlalchemy import exc


os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):

    def setUp(self):
        """Clear all tables and create user for messages."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(id=1, email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        self.u = u
        self.client = app.test_client()

    def tearDown(self):
        """Clear any failed commits."""
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="Test",
            user_id=1
        )

        db.session.add(m)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(m.text, "Test")
        self.assertEqual(m.user_id, 1)
        self.assertEqual(len(m.user.followers), 0)
        self.assertEqual(len(m.user.messages), 1)
        # Test __repr__
        self.assertEqual(m.__repr__(), f"<Message text={m.text}>")

    def test_message_likes(self):
        """Test that likes are only associated with correct user and only messages user likes are in liked."""
        m = Message(
            text='message',
            user_id=self.u.id
        )
        m.id = 1
        m2 = Message(
            text='message',
            user_id=self.u.id
        )
        m2.id = 2
        db.session.add(m, m2)
        db.session.commit()
        like = Likes(user_id=1, message_id=1)
        db.session.add(like)
        db.session.commit()
        # Test User liking messages works
        self.assertEqual(like.user_id, m.id)
        # Test message not liked are not shown
        self.assertNotEqual(like.user_id, m2.id)
        