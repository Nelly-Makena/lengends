
# Create your models here.
from django.db import models
from django.utils import timezone


class PaymentTransaction(models.Model):
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    checkout_request_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"


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
