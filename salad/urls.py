from django.urls import path
from salad.views import *
urlpatterns=[
    path("create-payment-intent/", CreatePaymentIntent.as_view(), name="create_payment_intent"),
    path("home-salad/", HomeSaladView.as_view(), name="home-salad"),
]