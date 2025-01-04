import stripe
from django.conf import settings
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView, status
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.


class CreatePaymentIntent(APIView):
    def post(self, request):
        try:
            data = request.data
            amount = data.get('amount',0)
            description = data.get("description", "Default description")
            customer_name = data.get("name")
            customer_address = data.get("address")
            currency= "inr"
            
            payment_intent = stripe.PaymentIntent.create(
                amount = amount,
                currency = currency,
                payment_method_types = ['card'],
                description=description,
                 shipping={
                    "name": customer_name,
                    "address": {
                        "line1": customer_address.get("line1"),
                        "city": customer_address.get("city"),
                        "state": customer_address.get("state"),
                        "postal_code": customer_address.get("postal_code"),
                        "country": customer_address.get("country"),
                    },}

            )

            return Response({"payment_intent_id":payment_intent['client_secret']},status=status.HTTP_200_OK)
        
        except Exception as e:
             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
