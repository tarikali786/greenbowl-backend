import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from salad.serializers import PaymentIntentSerializer
from salad.models import *
from django.db.models import Q
import uuid

from salad.serializers import *
from rest_framework.permissions import IsAuthenticated
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreatePaymentIntent(APIView):

    def post(self, request):
        serializer = PaymentIntentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=validated_data['amount'],
                currency="INR",
                payment_method_types=['card'],
                description="Order Salad",
                receipt_email=validated_data['email'],
                metadata={
                    "Name": validated_data['name'],
                    "Email": validated_data['email'],
                    "Phone": validated_data['phone'],
                },
                shipping={
                    "name": validated_data['name'],
                    "address": {
                        "line1": validated_data['address']['line1'],
                        "city": validated_data['address']['city'],
                        "state": validated_data['address']['state'],
                        "postal_code": validated_data['address']['postal_code'],
                        "country": validated_data['address']['country'],
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
        

class HomeSaladView(APIView):
    def get(self, request):
        base_ingredients = Ingredient.objects.filter(category='base')
        vegetable_ingredients = Ingredient.objects.filter(category='vegetable')
        topping_ingredients = Ingredient.objects.filter(category='topping')
        dressing_ingredients = Ingredient.objects.filter(category='dressing')
        extra_ingredients = Ingredient.objects.filter(category='extra')
        

        # Fetch salads by type
        most_loved_salads = Salad.objects.filter(salad_type="most_loved", available=True)
        popular_salads = Salad.objects.filter(salad_type="most_loved", available=True)

        # Serialize data
        data = {
            "base_ingredients": IngredientSerializer(base_ingredients, many=True).data,
            "vegetable_ingredients": IngredientSerializer(vegetable_ingredients, many=True).data,
            "topping_ingredients": IngredientSerializer(topping_ingredients, many=True).data,
            "vegetable_ingredients": IngredientSerializer(vegetable_ingredients, many=True).data,
            "dressing_ingredients": IngredientSerializer(dressing_ingredients, many=True).data,
            "extra_ingredients": IngredientSerializer(extra_ingredients, many=True).data,
            "most_loved_salads": SaladSerializer(most_loved_salads, many=True).data,
            "popular_salads": SaladSerializer(popular_salads, many=True).data,
        }
        
        return Response(data, status=status.HTTP_200_OK)
    

class RecipeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch all recipes of the logged-in user"""
        recipes = Recipe.objects.filter(user=request.user)
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        data = request.data.copy()
        data["user"] = request.user.id  

        serializer = RecipeSerializer(data=data, context={"request": request})  # ✅ Pass context here
        if serializer.is_valid():
            recipe = serializer.save(user=request.user)  
            return Response(RecipeSerializer(recipe).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





    def delete(self, request, uid):
        recipe = Recipe.objects.filter(uid=uid).first()
        print(recipe)
        
        if not recipe:
            return Response({'message': "Recipe Not Found"}, status=status.HTTP_404_NOT_FOUND)

        recipe.delete()
        return Response({'message': "Recipe deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



class OrderAPIView(APIView):

    permission_classes = [IsAuthenticated]


    def post(self, request):
        """Create a new order"""
        ingredient_uuids = request.data.get("ingredients", [])

        if not ingredient_uuids:
            return Response({"error": "At least one ingredient is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and filter valid UUIDs
        try:
            valid_uuids = [uuid.UUID(uid) for uid in ingredient_uuids]
        except ValueError:
            return Response({"error": "Invalid UUID format in ingredients."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch ingredients from the database
        ingredients = Ingredient.objects.filter(uid__in=valid_uuids)
        if len(ingredients) != len(valid_uuids):
            return Response({"error": "One or more ingredient UUIDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)

        # Create an Order
        order = Order.objects.create(
            user=request.user,
            total_price=request.data.get('total_price', 0),
            total_calories=request.data.get('total_calories', 0),
            status="placed",
            name=request.data.get('name', 'unnamed'),

        )

        # Assign ingredients to the order
        order.ingredients.set(ingredients)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    

class updateIngredientView(APIView):
    def get(self, request):
        data = Ingredient.objects.all()
        for i in data:
            i.weight = 500
            i.save()
 
        return Response("Some")
    