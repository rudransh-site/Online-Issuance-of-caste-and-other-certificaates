from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, OfficerProfile


class UserModelTest(TestCase):

    def setUp(self):
        self.citizen = User.objects.create_user(
            username='testcitizen', password='pass1234',
            role=User.CITIZEN, first_name='Test', last_name='Citizen'
        )
        self.officer_user = User.objects.create_user(
            username='testofficer', password='pass1234',
            role=User.OFFICER, first_name='Test', last_name='Officer'
        )
        self.admin_user = User.objects.create_user(
            username='testadmin', password='pass1234',
            role=User.ADMIN, first_name='Test', last_name='Admin'
        )

    def test_is_citizen_returns_true_for_citizen(self):
        self.assertTrue(self.citizen.is_citizen())

    def test_is_citizen_returns_false_for_officer(self):
        self.assertFalse(self.officer_user.is_citizen())

    def test_is_officer_returns_true_for_officer(self):
        self.assertTrue(self.officer_user.is_officer())

    def test_is_officer_returns_false_for_citizen(self):
        self.assertFalse(self.citizen.is_officer())

    def test_is_admin_returns_true_for_admin(self):
        self.assertTrue(self.admin_user.is_admin())

    def test_is_admin_returns_false_for_citizen(self):
        self.assertFalse(self.citizen.is_admin())

    def test_get_role_display_name_citizen(self):
        self.assertEqual(self.citizen.get_role_display_name(), 'Citizen')

    def test_get_role_display_name_officer(self):
        self.assertEqual(self.officer_user.get_role_display_name(), 'Revenue Officer')

    def test_get_role_display_name_admin(self):
        self.assertEqual(self.admin_user.get_role_display_name(), 'Revenue Admin')

    def test_default_role_is_citizen(self):
        user = User.objects.create_user(username='newuser', password='pass1234')
        self.assertEqual(user.role, User.CITIZEN)

    def test_str_representation(self):
        self.assertIn('testcitizen', str(self.citizen))
        self.assertIn('CITIZEN', str(self.citizen))


class OfficerProfileTest(TestCase):

    def setUp(self):
        self.officer_user = User.objects.create_user(
            username='officer1', password='pass1234', role=User.OFFICER
        )
        self.profile = OfficerProfile.objects.create(
            user=self.officer_user,
            designation='Revenue Officer',
            workload_count=0,
            is_active=True
        )

    def test_profile_created_successfully(self):
        self.assertEqual(self.profile.user.username, 'officer1')

    def test_default_workload_is_zero(self):
        self.assertEqual(self.profile.workload_count, 0)

    def test_is_active_default_true(self):
        self.assertTrue(self.profile.is_active)

    def test_is_flagged_default_false(self):
        self.assertFalse(self.profile.is_flagged)

    def test_get_completion_rate_zero_when_no_applications(self):
        rate = self.profile.get_completion_rate()
        self.assertEqual(rate, 0)

    def test_str_representation(self):
        self.assertIn('officer1', str(self.profile))


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.citizen = User.objects.create_user(
            username='citizen1', password='pass1234', role=User.CITIZEN
        )
        self.officer_user = User.objects.create_user(
            username='officer1', password='pass1234', role=User.OFFICER
        )
        OfficerProfile.objects.create(user=self.officer_user, is_active=True)
        self.admin_user = User.objects.create_user(
            username='admin1', password='pass1234', role=User.ADMIN
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_citizen_login_redirects_to_choose_certificate(self):
        response = self.client.post(reverse('login'), {
            'username': 'citizen1', 'password': 'pass1234'
        })
        self.assertRedirects(response, reverse('choose_certificate'))

    def test_officer_login_redirects_to_officer_list(self):
        response = self.client.post(reverse('login'), {
            'username': 'officer1', 'password': 'pass1234'
        })
        self.assertRedirects(response, reverse('officer_list'))

    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin1', 'password': 'pass1234'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'wronguser', 'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_logout_redirects_to_home(self):
        self.client.login(username='citizen1', password='pass1234')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))


class RegisterViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_successful_registration_creates_citizen(self):
        response = self.client.post(reverse('register'), {
            'username': 'newcitizen',
            'first_name': 'New',
            'last_name': 'Citizen',
            'email': 'new@test.com',
            'phone': '9999999999',
            'address': 'Test Address',
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        self.assertTrue(User.objects.filter(username='newcitizen').exists())
        user = User.objects.get(username='newcitizen')
        self.assertEqual(user.role, User.CITIZEN)

    def test_password_mismatch_shows_error(self):
        response = self.client.post(reverse('register'), {
            'username': 'newcitizen2',
            'first_name': 'New',
            'last_name': 'Citizen',
            'email': 'new2@test.com',
            'password1': 'TestPass@123',
            'password2': 'WrongPass@123',
        })
        self.assertFalse(User.objects.filter(username='newcitizen2').exists())
