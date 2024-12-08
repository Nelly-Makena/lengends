from django.contrib import admin
from django.urls import path
from events.views import thank_you_view, register_event_view
from events.callback import MpesaExpressCallback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', register_event_view, name='register_event'),
    path('thank-you/', thank_you_view, name='thank_you'),
    path('payment/callback/', MpesaExpressCallback.as_view(), name='mpesa_callback'),]
