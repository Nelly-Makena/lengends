from django.contrib import admin

# Register your models here.
from .models import EventRegistration,MpesaTransaction

class MpesaTransactionAdmin(admin.ModelAdmin):
    pass  # Add any customizations to the admin here if needed


class EventRegistrationAdmin(admin.ModelAdmin):
    pass  # Add any customizations to the admin here if needed

admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(MpesaTransaction,MpesaTransactionAdmin)
