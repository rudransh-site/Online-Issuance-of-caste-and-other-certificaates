from django.db import models
from django.utils import timezone
from users.models import User, OfficerProfile


class CertificateApplication(models.Model):
    SUBMITTED = 'SUBMITTED'
    ASSIGNED = 'ASSIGNED'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    OVERDUE = 'OVERDUE'

    STATUS_CHOICES = [
        (SUBMITTED, 'Submitted'),
        (ASSIGNED, 'Assigned'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (OVERDUE, 'Overdue'),
    ]

    CASTE = 'CASTE'
    INCOME = 'INCOME'
    BIRTH = 'BIRTH'
    DEATH = 'DEATH'

    CERTIFICATE_CHOICES = [
        (CASTE, 'Caste Certificate'),
        (INCOME, 'Income Certificate'),
        (BIRTH, 'Birth Certificate'),
        (DEATH, 'Death Certificate'),
    ]

    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    assigned_officer = models.ForeignKey(
        OfficerProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_applications'
    )
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=SUBMITTED)

    # Common mandatory
    applicant_name = models.CharField(max_length=100)
    applicant_dob = models.DateField()
    applicant_gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')
    ])
    applicant_phone = models.CharField(max_length=15)
    applicant_address = models.TextField()
    aadhar_number = models.CharField(max_length=12)
    aadhar_photo = models.ImageField(upload_to='aadhar/%Y/%m/', null=True, blank=True)

    # Caste specific
    caste_name = models.CharField(max_length=100, blank=True)
    caste_category = models.CharField(max_length=10, blank=True, choices=[
        ('SC', 'SC'), ('ST', 'ST'), ('OBC', 'OBC'), ('General', 'General'),
    ])
    father_name = models.CharField(max_length=100, blank=True)
    purpose = models.TextField(blank=True)

    # Income specific
    annual_income = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    income_purpose = models.TextField(blank=True)

    # Birth specific
    birth_place = models.CharField(max_length=200, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    birth_father_name = models.CharField(max_length=100, blank=True)
    hospital_name = models.CharField(max_length=200, blank=True)

    # Death specific
    deceased_name = models.CharField(max_length=100, blank=True)
    death_date = models.DateField(null=True, blank=True)
    death_place = models.CharField(max_length=200, blank=True)
    cause_of_death = models.CharField(max_length=200, blank=True)
    informant_name = models.CharField(max_length=100, blank=True)
    relation_to_deceased = models.CharField(max_length=50, blank=True)

    submitted_date = models.DateTimeField(default=timezone.now)
    assigned_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_date']

    def is_overdue(self):
        if self.status == self.ASSIGNED and self.due_date:
            return timezone.now() > self.due_date
        return False

    def days_remaining(self):
        if self.due_date and self.status in [self.ASSIGNED, self.OVERDUE]:
            delta = self.due_date - timezone.now()
            return delta.days
        return None

    def __str__(self):
        return f"#{self.id} — {self.applicant_name} — {self.certificate_type} — {self.status}"
