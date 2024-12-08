import pytz
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .models import MpesaTransaction
import logging
from django.utils.timezone import now
from rest_framework.decorators import api_view

transaction_date = now()

# Configure logging
logger = logging.getLogger(__name__)



class MpesaExpressCallback(APIView):
    def post(self, request, *args, **kwargs):
        try:
            logger.debug("Received M-Pesa Callback: %s", request.data)

            # Extract data from callback
            stk_callback = request.data.get("Body", {}).get("stkCallback", {})
            merchant_request_id = stk_callback.get("MerchantRequestID")
            checkout_request_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")
            result_desc = stk_callback.get("ResultDesc")

            # Extract metadata items
            items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            amount = None
            phone_number = None
            mpesa_receipt_number = None
            transaction_date = None

            for item in items:
                if item.get("Name") == "Amount":
                    amount = item.get("Value")
                elif item.get("Name") == "MpesaReceiptNumber":
                    mpesa_receipt_number = item.get("Value")
                elif item.get("Name") == "PhoneNumber":
                    phone_number = item.get("Value")
                elif item.get("Name") == "TransactionDate":
                    transaction_date = item.get("Value")

            # Convert transaction date to timezone-aware datetime
            if transaction_date:
                transaction_datetime = datetime.strptime(
                    str(transaction_date), "%Y%m%d%H%M%S"
                )
                transaction_datetime = pytz.utc.localize(transaction_datetime)
            else:
                transaction_datetime = None

            logger.info(
                "Parsed Callback Data: Amount=%s, PhoneNumber=%s, ReceiptNumber=%s, TransactionDate=%s",
                amount,
                phone_number,
                mpesa_receipt_number,
                transaction_datetime,
            )

            # Save transaction to database
            mpesa_payment = MpesaTransaction.objects.create(
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id,
                amount=amount,
                phone_number=phone_number,
                result_code=result_code,
                result_desc=result_desc,
                mpesa_receipt_number=mpesa_receipt_number,
                transaction_date=transaction_datetime,
                status="Success" if result_code == 0 else "Failed",
                callback_url=request.build_absolute_uri(),
            )
            logger.info("M-Pesa Payment Saved: %s", mpesa_payment)

            return Response({"status": "success", "message": "Payment recorded successfully!"}, status=HTTP_200_OK)

        except KeyError as e:
            logger.error("KeyError while processing M-Pesa callback: %s", e)
            return Response(
                {"error": "Invalid callback data", "details": str(e)},
                status=HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception("An error occurred while processing M-Pesa callback")
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=HTTP_400_BAD_REQUEST,
            )