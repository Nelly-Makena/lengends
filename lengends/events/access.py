import base64
import requests

def get_access_token():
    consumer_key = "7H7VKVLFzPXAACuGAAA6LJD24D84X98SUGtAL4rWhS2WMIS7"
    consumer_secret = "bLz8mEADcgAbrFv11rjuWkwGXnNaAH1zCsuKBAkMXbrlrXuGhbfROtkZPoL5H7qb"
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # Encode the credentials using base64
    auth_string = f"{consumer_key}:{consumer_secret}"
    encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {encoded_auth}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP codes >= 400
        data = response.json()
        if "access_token" in data:
            return data["access_token"]
        else:
            raise ValueError("Access token not found in response")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")
        raise
    except ValueError as ve:
        print(f"Unexpected response format: {ve}")
        raise
