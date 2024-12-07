from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.timezone import now
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
from .forms import EventRegistrationForm
from .models import PaymentTransaction


# Function to retrieve access token
def get_access_token():
    consumer_key = "7H7VKVLFzPXAACuGAAA6LJD24D84X98SUGtAL4rWhS2WMIS7"
    consumer_secret = "bLz8mEADcgAbrFv11rjuWkwGXnNaAH1zCsuKBAkMXbrlrXuGhbfROtkZPoL5H7qb"

    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = HTTPBasicAuth(consumer_key, consumer_secret)

    response = requests.get(api_url, auth=auth)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Failed to get access token: {response.text}")
        return None


# Function to get the dynamic Ngrok URL
def get_ngrok_url():
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        response.raise_for_status()
        tunnels = response.json().get('tunnels', [])
        if tunnels:
            return tunnels[0].get('public_url')
    except requests.RequestException as e:
        print(f"Error fetching Ngrok URL: {e}")
    return None


# Function to initiate STK push
def initiate_stk_push(phone_number, amount):
    access_token = get_access_token()
    if access_token:
        business_short_code = "174379"
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

        # Dynamically retrieve the callback URL
        ngrok_url = get_ngrok_url()
        if not ngrok_url:
            print("Failed to retrieve Ngrok URL.")
            return False

        callback_url = f"{ngrok_url}/payment_callback/"

        # Print the callback URL for debugging
        print(f"Callback URL: {callback_url}")

        process_request_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        # Timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        # Encode password
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

        stk_push_headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json',
        }

        stk_push_payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": "LENGENDARY TABLE",
            "TransactionDesc": "Event Push Test",
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("ResponseCode") == "0":
                print(f"STK Push sent successfully. CheckoutRequestID: {response_data.get('CheckoutRequestID')}")
                return True
            else:
                print(f"STK Push failed: {response_data.get('errorMessage')}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error sending STK push: {str(e)}")
            return False
    else:
        print("Access token not found.")
        return False


# Event registration view
def register_event_view(request):
    if request.method == "POST":
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            # Save the form data if valid
            form.save()
            phone_number = form.cleaned_data['phone_number']  # Get phone number from form
            amount = 1  # The set amount, change this later
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


# Payment callback view
def payment_callback_view(request):
    if request.method == 'POST':
        try:
            data = request.POST
            transaction_id = data.get('TransactionID')
            amount = data.get('Amount')
            status = data.get('Status')
            checkout_request_id = data.get('CheckoutRequestID')

            # Check if required data exists
            if not all([transaction_id, amount, status, checkout_request_id]):
                return JsonResponse({"status": "error", "message": "Missing required data"}, status=400)

            # Check if the transaction already exists in the database to prevent duplicates
            payment = PaymentTransaction.objects.filter(transaction_id=transaction_id).first()
            if payment:
                return JsonResponse({"status": "error", "message": "Duplicate transaction detected"}, status=400)

            # Create a new payment transaction
            payment = PaymentTransaction(
                transaction_id=transaction_id,
                amount=amount,
                status=status,
                checkout_request_id=checkout_request_id
            )
            payment.save()

            # Return a success response
            return JsonResponse({
                "status": "success",
                "message": "Payment processed successfully",
                "transaction_id": transaction_id,
                "amount": amount,
                "status": status
            })

        except Exception as e:
            # Log the exception for debugging
            print(f"Error processing payment callback: {str(e)}")
            return JsonResponse({"status": "error", "message": "Failed to process payment"}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
