from django.urls import path
from account.views import *
urlpatterns=[
   path('google-login/', GoogleLogin.as_view(), name='google-login'),
   path('account-googlelogin/', AccountGoogleLogin.as_view(), name='google-login'),
   path('account-register/', RegisterAccountView.as_view(), name='account-register'),
   path('account-login/', LoginView.as_view(), name='account-login'),
   path('send-otp/', SendOTPCode.as_view(), name='send-otp'),
   path('verify-otp/', VerifyOTPCode.as_view(), name='verify-otp'),
   path('create-user-address/', UserAddressViewSet.as_view({"get": "list", "post": "create"}), name='user-address'),
   path("user-address/<uuid:uid>/", UserAddressViewSet.as_view({"get": "retrieve",  "patch": "partial_update", "delete": "destroy"})),
]