from django.test import TestCase, Client
from django.urls import reverse
from users.models import User, OfficerProfile
from applications.models import CertificateApplication
from automation.models import AuditLog
from automation.services import AssignmentService, ProcessingService


def make_admin(username='admin1'):
    return User.objects.create_user(
        username=username, password='pass1234',
        role=User.ADMIN, first_name='Revenue', last_name='Admin'
    )

def make_officer(username='officer1'):
    user = User.objects.create_user(
        username=username, password='pass1234',
        role=User.OFFICER, first_name='Test', last_name='Officer'
    )
    profile = OfficerProfile.objects.create(
        user=user, designation='Revenue Officer',
        workload_count=0, is_active=True
    )
    return user, profile

def make_citizen(username='citizen1'):
    return User.objects.create_user(
        username=username, password='pass1234', role=User.CITIZEN
    )

def make_application(citizen, cert_type='CASTE'):
    return CertificateApplication.objects.create(
        citizen=citizen, certificate_type=cert_type,
        applicant_name='Test Applicant', applicant_dob='2000-01-01',
        applicant_gender='Male', applicant_phone='9999999999',
        applicant_address='Test Address', aadhar_number='123456789012',
        status=CertificateApplication.SUBMITTED,
    )


class AdminDashboardTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin1', password='pass1234')

    def test_dashboard_loads(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_shows_correct_total(self):
        citizen = make_citizen()
        officer_user, profile = make_officer()
        make_application(citizen)
        make_application(citizen, 'INCOME')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.context['total'], 2)

    def test_dashboard_shows_correct_approved_count(self):
        citizen = make_citizen()
        officer_user, profile = make_officer()
        app = make_application(citizen)
        AssignmentService.assign_application(app)
        app.refresh_from_db()
        ProcessingService.approve_application(app, officer_user, 'Approved')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.context['approved'], 1)

    def test_dashboard_shows_correct_rejected_count(self):
        citizen = make_citizen()
        officer_user, profile = make_officer()
        app = make_application(citizen)
        AssignmentService.assign_application(app)
        app.refresh_from_db()
        ProcessingService.reject_application(app, officer_user, 'Wrong details')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.context['rejected'], 1)

    def test_dashboard_completion_pct_zero_when_no_apps(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.context['completion_pct'], 0)

    def test_dashboard_completion_pct_correct(self):
        citizen = make_citizen()
        officer_user, profile = make_officer()
        app1 = make_application(citizen)
        app2 = make_application(citizen, 'INCOME')
        AssignmentService.assign_application(app1)
        app1.refresh_from_db()
        ProcessingService.approve_application(app1, officer_user, 'OK')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.context['completion_pct'], 50.0)

    def test_citizen_cannot_access_dashboard(self):
        citizen_client = Client()
        citizen = make_citizen('citizen_test')
        citizen_client.login(username='citizen_test', password='pass1234')
        response = citizen_client.get(reverse('admin_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_officer_cannot_access_dashboard(self):
        officer_client = Client()
        officer_user, profile = make_officer()
        officer_client.login(username='officer1', password='pass1234')
        response = officer_client.get(reverse('admin_dashboard'))
        self.assertNotEqual(response.status_code, 200)


class ManageOfficersTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin1', password='pass1234')

    def test_manage_officers_page_loads(self):
        response = self.client.get(reverse('manage_officers'))
        self.assertEqual(response.status_code, 200)

    def test_create_officer_successfully(self):
        response = self.client.post(reverse('manage_officers'), {
            'username': 'newofficer',
            'password': 'pass1234',
            'first_name': 'New',
            'last_name': 'Officer',
            'email': 'officer@test.com',
            'designation': 'Revenue Officer',
        })
        self.assertTrue(User.objects.filter(username='newofficer').exists())
        user = User.objects.get(username='newofficer')
        self.assertEqual(user.role, User.OFFICER)
        self.assertTrue(OfficerProfile.objects.filter(user=user).exists())

    def test_create_officer_without_username_fails(self):
        count_before = User.objects.count()
        self.client.post(reverse('manage_officers'), {
            'username': '',
            'password': 'pass1234',
        })
        self.assertEqual(User.objects.count(), count_before)

    def test_duplicate_username_not_created(self):
        make_officer('existing_officer')
        count_before = User.objects.count()
        self.client.post(reverse('manage_officers'), {
            'username': 'existing_officer',
            'password': 'pass1234',
        })
        self.assertEqual(User.objects.count(), count_before)

    def test_toggle_officer_active_status(self):
        officer_user, profile = make_officer()
        self.assertTrue(profile.is_active)
        self.client.post(reverse('toggle_officer', args=[profile.pk]))
        profile.refresh_from_db()
        self.assertFalse(profile.is_active)

    def test_toggle_officer_back_to_active(self):
        officer_user, profile = make_officer()
        profile.is_active = False
        profile.save()
        self.client.post(reverse('toggle_officer', args=[profile.pk]))
        profile.refresh_from_db()
        self.assertTrue(profile.is_active)

    def test_add_remark_to_officer(self):
        officer_user, profile = make_officer()
        self.client.post(reverse('add_remark', args=[profile.pk]), {
            'remark': 'Excellent performance this month'
        })
        profile.refresh_from_db()
        self.assertEqual(profile.admin_remarks, 'Excellent performance this month')

    def test_flag_officer(self):
        officer_user, profile = make_officer()
        self.assertFalse(profile.is_flagged)
        self.client.post(reverse('flag_officer', args=[profile.pk]), {
            'reason': 'High performer'
        })
        profile.refresh_from_db()
        self.assertTrue(profile.is_flagged)

    def test_unflag_officer(self):
        officer_user, profile = make_officer()
        profile.is_flagged = True
        profile.flag_reason = 'High performer'
        profile.save()
        self.client.post(reverse('flag_officer', args=[profile.pk]), {'reason': ''})
        profile.refresh_from_db()
        self.assertFalse(profile.is_flagged)


class AllApplicationsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin1', password='pass1234')
        self.citizen = make_citizen()

    def test_all_applications_page_loads(self):
        response = self.client.get(reverse('all_applications'))
        self.assertEqual(response.status_code, 200)

    def test_all_applications_shows_all(self):
        make_application(self.citizen)
        make_application(self.citizen, 'INCOME')
        response = self.client.get(reverse('all_applications'))
        self.assertEqual(response.context['total'], 2)

    def test_filter_by_status_approved(self):
        officer_user, profile = make_officer()
        app1 = make_application(self.citizen)
        app2 = make_application(self.citizen, 'INCOME')
        AssignmentService.assign_application(app1)
        app1.refresh_from_db()
        ProcessingService.approve_application(app1, officer_user, 'OK')
        response = self.client.get(reverse('all_applications') + '?status=APPROVED')
        apps = list(response.context['applications'])
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0].status, 'APPROVED')

    def test_filter_by_status_overdue(self):
        from django.utils import timezone
        from datetime import timedelta
        from automation.services import OverdueService
        officer_user, profile = make_officer()
        app = make_application(self.citizen)
        AssignmentService.assign_application(app)
        app.refresh_from_db()
        app.due_date = timezone.now() - timedelta(hours=2)
        app.save()
        OverdueService.check_and_mark_overdue()
        response = self.client.get(reverse('all_applications') + '?status=OVERDUE')
        apps = list(response.context['applications'])
        self.assertEqual(len(apps), 1)


class AuditLogViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin1', password='pass1234')

    def test_audit_log_page_loads(self):
        response = self.client.get(reverse('audit_log'))
        self.assertEqual(response.status_code, 200)

    def test_audit_log_shows_entries(self):
        AuditLog.objects.create(
            performed_by=self.admin,
            action='LOGIN',
            description='admin logged in'
        )
        response = self.client.get(reverse('audit_log'))
        logs = response.context['logs']
        self.assertGreater(logs.count(), 0)

    def test_audit_log_blocked_for_non_admin(self):
        citizen_client = Client()
        citizen = make_citizen('audit_citizen')
        citizen_client.login(username='audit_citizen', password='pass1234')
        response = citizen_client.get(reverse('audit_log'))
        self.assertNotEqual(response.status_code, 200)
