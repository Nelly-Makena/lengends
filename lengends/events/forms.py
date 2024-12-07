from django import forms
from events.models import EventRegistration
from django.core.exceptions import ValidationError

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['name', 'phone_number', 'email', 'is_campus_student', 'school_name']

    is_campus_student = forms.ChoiceField(
        choices=EventRegistration.YES_NO_CHOICES,
        widget=forms.RadioSelect,
        label="Are you a campus student?",
        required=True
    )
    school_name = forms.CharField(
        required=False,
        label="If yes, which school do you attend?",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your university name'}),
    )

    # Custom phone number cleaning
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        # Ensure the phone number starts with '254' or adjust it
        if phone_number.startswith('0'):
            # Remove leading zero and add country code '254'
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            # If it doesn't start with 254, raise a validation error
            raise ValidationError("Phone number must start with 254.")

        # Optional: Check if phone number has valid length (12 digits including country code)
        if len(phone_number) != 12:  # +254 plus 9 digits for local numbers
            raise ValidationError("Phone number must have 12 digits including country code (254).")

        # Return the cleaned phone number
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        is_campus_student = cleaned_data.get("is_campus_student")
        school_name = cleaned_data.get("school_name")

        # Validation for campus student and school name
        if is_campus_student == 'yes' and not school_name:
            self.add_error('school_name', 'Please provide your school name.')

        return cleaned_data
