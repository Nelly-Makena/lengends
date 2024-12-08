
# Create your models here.
from django.db import models
from django.utils import timezone
from django.utils.timezone import now


class MpesaTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=255, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=255, null=True, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('Success', 'Success'), ('Failed', 'Failed')], default='Failed')
    callback_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"M-Pesa Transaction {self.mpesa_receipt_number or 'N/A'} - {self.status}"

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
