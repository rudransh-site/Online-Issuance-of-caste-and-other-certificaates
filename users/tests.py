from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTest(TestCase):

    def test_create_citizen_user(self):
        user = User.objects.create_user(
            username="citizen1",
            password="test123",
            role="CITIZEN"
        )
        self.assertEqual(user.role, "CITIZEN")

    def test_create_officer_user(self):
        user = User.objects.create_user(
            username="officer1",
            password="test123",
            role="OFFICER"
        )
        self.assertEqual(user.role, "OFFICER")

    def test_create_admin_user(self):
        user = User.objects.create_user(
            username="admin1",
            password="test123",
            role="ADMIN"
        )
        self.assertEqual(user.role, "ADMIN")