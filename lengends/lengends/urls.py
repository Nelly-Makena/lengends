from django.contrib import admin
from django.urls import path
from events.views import thank_you_view, register_event_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register-event/', register_event_view, name='register_event'),
    path('thank-you/', thank_you_view, name='thank_you'),  # Thank You page URL
]
