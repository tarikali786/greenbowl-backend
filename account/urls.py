from django.urls import path
from account.views import *
urlpatterns=[
   path('google-login/', GoogleLogin.as_view(), name='google-login'),
   path('account-googlelogin/', AccountGoogleLogin.as_view(), name='google-login'),
   path('account-register/', RegisterAccountView.as_view(), name='account-register'),
   path('account-login/', LoginView.as_view(), name='account-login'),
   path('send-otp/', SendOTPCode.as_view(), name='send-otp'),
   path('verify-otp/', VerifyOTPCode.as_view(), name='verify-otp')
]