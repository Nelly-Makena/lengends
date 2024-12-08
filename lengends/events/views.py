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
from django.views.decorators.csrf import csrf_exempt
import logging





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

        # Dynamically retrieving  the callback URL
        ngrok_url = get_ngrok_url()
        if not ngrok_url:
            print("Failed to retrieve Ngrok URL.")
            return False

        callback_url = f"{ngrok_url}/payment_callback/"

        #  for debugging the call back url
        print(f"Callback URL: {callback_url}")

        process_request_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        # Timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        #  password
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


# Payment callback view
@csrf_exempt
def payment_callback_view(request):
    log_file = "Mpesastkresponse.json"

    if request.method == 'POST':
        try:
            # Parse the incoming JSON request body
            stk_callback_response = json.loads(request.body)

            # Log the response data to a file for debugging
            with open(log_file, "a") as log:
                json.dump(stk_callback_response, log)
                log.write("\n")  # new line

            # Extract the necessary data from the response
            merchant_request_id = stk_callback_response.get('Body', {}).get('stkCallback', {}).get('MerchantRequestID')
            checkout_request_id = stk_callback_response.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            result_code = stk_callback_response.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            result_desc = stk_callback_response.get('Body', {}).get('stkCallback', {}).get('ResultDesc')

            # Safe access for CallbackMetadata and its items
            callback_metadata = stk_callback_response.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata',
                                                                                                 {}).get('Item', [])

            # Initialize the variables to None
            amount = None
            transaction_id = None
            user_phone_number = None

            # Check if CallbackMetadata exists and contains items
            if callback_metadata:
                for item in callback_metadata:
                    if item.get('Name') == 'Amount':
                        amount = item.get('Value')
                    elif item.get('Name') == 'TransID':
                        transaction_id = item.get('Value')
                    elif item.get('Name') == 'PhoneNumber':
                        user_phone_number = item.get('Value')

            # Ensure all necessary data is present
            if not all([merchant_request_id, checkout_request_id, result_code, result_desc, amount, transaction_id,
                        user_phone_number]):
                return JsonResponse({"status": "error", "message": "Missing required data"}, status=400)

            # Check if the payment was successful
            if result_code == 0:
                # Store the transaction details in the database
                payment = PaymentTransaction(
                    merchant_request_id=merchant_request_id,
                    checkout_request_id=checkout_request_id,
                    result_code=result_code,
                    result_desc=result_desc,
                    amount=amount,
                    transaction_id=transaction_id,
                    user_phone_number=user_phone_number,
                )
                payment.save()

                # Return a success response
                return JsonResponse({
                    "status": "success",
                    "message": "Payment processed successfully",
                    "MerchantRequestID": merchant_request_id,
                    "CheckoutRequestID": checkout_request_id,
                    "ResponseCode": result_code,
                    "ResponseDescription": result_desc,
                    "CustomerMessage": "Success. Request accepted for processing"
                })

            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Payment failed: {result_desc}"
                }, status=400)

        except Exception as e:
            logging.error(f"Error processing payment callback: {str(e)}")
            return JsonResponse({"status": "error", "message": "Failed to process payment"}, status=500)

    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
