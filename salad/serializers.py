from rest_framework import serializers
from .models import Ingredient, Salad, Order, Recipe

class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    address = serializers.DictField(child=serializers.CharField(), required=True)




class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'  # Includes all model fields

class SaladSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)  # Nested serializer for ingredients

    class Meta:
        model = Salad
        fields = '__all__'  # Includes all model fields


class UserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields ='__all__'


class RecipeSerializer(serializers.ModelSerializer):
   
    ingredients = IngredientSerializer(many=True, read_only=True)
    class Meta:
        model = Recipe
        fields = ['uid', 'name', 'user', 'ingredients', 'total_price']
        extra_kwargs = {'user': {'read_only': True}}


class OrderSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Order  # FIXED: Changed from Recipe to Order
        fields = ['uid', 'user', 'ingredients', 'total_price', 'total_calories', 'status', 'created_at']
        extra_kwargs = {'user': {'read_only': True}}