from django.urls import path
from salad.views import *
urlpatterns=[
    path("create-payment-intent/", CreatePaymentIntent.as_view(), name="create_payment_intent"),
    path("home-salad/", HomeSaladView.as_view(), name="home-salad"),
    path("recipe/", RecipeAPIView.as_view(), name="recipe"),
    path("recipe/<uuid:uid>/", RecipeAPIView.as_view(), name="recipe-detail"),  # For DELETE
    path("recipe-details/<uuid:uid>/", GetRecipeDetails.as_view(), name="recipe-detail"),  # For get single item
    path("order/", OrderAPIView.as_view(), name="order"),
    path("update/", updateIngredientView.as_view(), name="update"),


]