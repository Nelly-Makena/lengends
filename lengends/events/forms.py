from django import forms
from events.models import EventRegistration

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

    def clean(self):
        cleaned_data = super().clean()
        is_campus_student = cleaned_data.get("is_campus_student")
        school_name = cleaned_data.get("school_name")

        # Validation for campus student and school name
        if is_campus_student == 'yes' and not school_name:
            self.add_error('school_name', 'Please provide your school name.')

        return cleaned_data
