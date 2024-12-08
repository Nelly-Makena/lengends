from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
from .forms import EventRegistrationForm
from .access import get_access_token
from .STKpush import initiate_stk_push,generate_password
from .callback import MpesaExpressCallback
# Event registration view
def register_event_view(request):
    if request.method == "POST":
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            # Saves the form data if valid
            form.save()
            phone_number = form.cleaned_data['phone_number']  # Get phone number from the  form
            amount = 1  # The set amount,  i will change this later
            stk_push_success = initiate_stk_push(phone_number, amount)

            # Redirect to the thank you page if the STK push is successful
            if stk_push_success:
                return redirect('thank_you')
            else:
                # Error message if STK push fails
                messages.error(request, "Payment failed. Please try again.")
                return render(request, 'register_event.html', {'form': form})
    else:
        form = EventRegistrationForm()

    return render(request, 'register_event.html', {'form': form})


# Thank you view
def thank_you_view(request):
    return render(request, 'thank_you.html')


