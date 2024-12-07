from django.contrib import admin
from django.urls import path
from events.views import thank_you_view, register_event_view, payment_callback_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', register_event_view, name='register_event'),
    path('thank-you/', thank_you_view, name='thank_you'),
    path('payment_callback/', payment_callback_view, name='payment_callback'),  # Fixed space here
]
