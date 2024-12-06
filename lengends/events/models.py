
# Create your models here.
from django.db import models


class EventRegistration(models.Model):
    # Choices for the 'Are you a student?' field
    YES_NO_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    is_campus_student = models.CharField(
        max_length=3, choices=YES_NO_CHOICES, default='no'
    )
    school_name = models.CharField(
        max_length=255, blank=True, null=True
    )

    def __str__(self):
        return self.name
