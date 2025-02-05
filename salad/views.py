import stripe
from django.conf import settings
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView, status
from salad.serializers import PaymentIntentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.



class CreatePaymentIntent(APIView):
    def post(self, request):
        serializer = PaymentIntentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=validated_data['amount'],
                currency=validated_data['currency'],
                payment_method_types=['card'],
                description=validated_data['description'],
                receipt_email=validated_data['email'],
                metadata={
                    "First Name": validated_data['fname'],
                    "Last Name": validated_data['lname'],
                    "Email": validated_data['email'],
                    "Phone": validated_data['phone'],
                    "Company Name": validated_data.get('company_name', ''),
                },
                shipping={
                    "name": f"{validated_data['fname']} {validated_data['lname']}",
                    "address": {
                        "line1": validated_data['address'].get('line1', ''),
                        "city": validated_data['address'].get('city', ''),
                        "state": validated_data['address'].get('state', ''),
                        "postal_code": validated_data['address'].get('postal_code', ''),
                        "country": validated_data['address'].get('country', ''),
                    },
                }
            )
            return Response({"payment_intent_id": payment_intent['client_secret']}, status=status.HTTP_200_OK)
        
        except stripe.error.CardError as e:
            return Response({"error": f"Card error: {e.user_message}"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            return Response({"error": "Payment service error. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
