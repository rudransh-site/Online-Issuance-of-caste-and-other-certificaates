from django.test import TestCase
from users.models import User, OfficerProfile
from applications.models import CertificateApplication

class AdminPanelTest(TestCase):

    def test_officer_application_count(self):
        # Step 1: Create User
        officer_user = User.objects.create_user(
            username="officer1",
            password="test123",
            role="OFFICER"
        )

        # Step 2: Create OfficerProfile
        officer_profile = OfficerProfile.objects.create(
            user=officer_user
        )

        # Step 3: Create Application with OfficerProfile
        CertificateApplication.objects.create(
            application_type="CASTE",
            status="ASSIGNED",
            assigned_officer=officer_profile
        )

        # Step 4: Count applications
        count = CertificateApplication.objects.filter(
            assigned_officer=officer_profile
        ).count()

        self.assertEqual(count, 1)