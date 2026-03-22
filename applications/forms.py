from django import forms
from applications.models import CertificateApplication


AADHAR_WIDGET = forms.TextInput(attrs={
    'placeholder': 'Enter 12-digit Aadhaar number',
    'maxlength': '12', 'minlength': '12', 'pattern': '[0-9]{12}'
})


class BaseApplicationForm(forms.ModelForm):
    """Common fields for all certificate types."""
    class Meta:
        model = CertificateApplication
        fields = [
            'applicant_name', 'applicant_dob', 'applicant_gender',
            'applicant_phone', 'applicant_address', 'aadhar_number', 'aadhar_photo',
        ]
        widgets = {
            'applicant_address': forms.Textarea(attrs={'rows': 2}),
            'applicant_dob': forms.DateInput(attrs={'type': 'date'}),
            'aadhar_number': AADHAR_WIDGET,
        }

    def clean_aadhar_number(self):
        val = self.cleaned_data.get('aadhar_number', '').strip()
        if not val.isdigit() or len(val) != 12:
            raise forms.ValidationError("Aadhaar number must be exactly 12 digits.")
        return val


class CasteCertificateForm(BaseApplicationForm):
    class Meta(BaseApplicationForm.Meta):
        fields = BaseApplicationForm.Meta.fields + [
            'caste_name', 'caste_category', 'father_name', 'purpose'
        ]
        widgets = {
            **BaseApplicationForm.Meta.widgets,
            'purpose': forms.Textarea(attrs={'rows': 2}),
        }


class IncomeCertificateForm(BaseApplicationForm):
    class Meta(BaseApplicationForm.Meta):
        fields = BaseApplicationForm.Meta.fields + [
            'annual_income', 'occupation', 'income_purpose'
        ]
        widgets = {
            **BaseApplicationForm.Meta.widgets,
            'annual_income': forms.TextInput(attrs={'placeholder': 'e.g. 150000'}),
            'income_purpose': forms.Textarea(attrs={'rows': 2}),
        }


class BirthCertificateForm(BaseApplicationForm):
    class Meta(BaseApplicationForm.Meta):
        fields = BaseApplicationForm.Meta.fields + [
            'birth_place', 'mother_name', 'birth_father_name', 'hospital_name'
        ]


class DeathCertificateForm(BaseApplicationForm):
    class Meta(BaseApplicationForm.Meta):
        fields = BaseApplicationForm.Meta.fields + [
            'deceased_name', 'death_date', 'death_place',
            'cause_of_death', 'informant_name', 'relation_to_deceased'
        ]
        widgets = {
            **BaseApplicationForm.Meta.widgets,
            'death_date': forms.DateInput(attrs={'type': 'date'}),
        }


class OfficerDecisionForm(forms.Form):
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter remarks (mandatory for rejection, optional for approval)...'
        }),
        required=False
    )
