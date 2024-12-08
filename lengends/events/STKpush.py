import requests
import base64
import datetime
from .access import get_access_token

def generate_password(shortcode, passkey, timestamp):
    password_string = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(password_string.encode('utf-8')).decode('utf-8')

def initiate_stk_push(phone_number, amount):
    try:
        # Mpesa credentials
        shortcode = '174379'
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        callback_url = "https://5e8a-197-136-53-2.ngrok-free.app/payment/callback/"
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password = generate_password(shortcode, passkey, timestamp)

        # Payload for the API
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": "1",
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": "TestPayment",
            "TransactionDesc": "Payment for services"
        }

        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status Code: {response.status_code}, Error: {response.text}"}

    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
