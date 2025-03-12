from rest_framework import serializers
from .models import Ingredient, Salad, Order, Recipe, RecipeIngredients

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

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)  
    class Meta:
        model = RecipeIngredients
        fields = ['ingredient', 'weight', 'price', 'calories']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='recipe_ingredients', many=True, read_only=True)  # ✅ Fetch related ingredients

    class Meta:
        model = Recipe
        fields = ['uid', 'name', 'user', 'total_price', 'total_calories', 'ingredients']
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        ingredients_data = self.initial_data.get("ingredients", [])  # ✅ Directly get from request data
        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients_data:
            try:
                ingredient = Ingredient.objects.get(uid=item['ingredient_id'])
                RecipeIngredients.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    weight=item['weight'],
                    price=item['price'],
                    calories=item['calories']
                )
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(f"Ingredient with ID {item['ingredient_id']} does not exist.")

        return recipe


    



class OrderSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Order  # FIXED: Changed from Recipe to Order
        fields = ['uid', 'user', 'ingredients', 'total_price', 'total_calories', 'status', 'created_at']
        extra_kwargs = {'user': {'read_only': True}}