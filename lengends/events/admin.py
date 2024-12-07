from django.contrib import admin

# Register your models here.
from .models import PaymentTransaction, EventRegistration

class PaymentTransactionAdmin(admin.ModelAdmin):
    pass  # Add any customizations to the admin here if needed

class EventRegistrationAdmin(admin.ModelAdmin):
    pass  # Add any customizations to the admin here if needed

admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
admin.site.register(EventRegistration, EventRegistrationAdmin)
