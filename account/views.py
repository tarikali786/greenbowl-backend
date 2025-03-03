from django.core.exceptions import ValidationError
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from account.models import Account  
from rest_framework.permissions import AllowAny,IsAuthenticated
from account.serializers import *
from django.db.models import Q
from rest_framework import status
import datetime
from rest_framework import viewsets
import pytz
from core.utils import  generate_otp, store_otp, get_stored_otp, send_otp_sms
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.core.cache import cache

    
OTP_EXPIRATION_MINUTES = 5
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')
class GoogleLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            email = data.get("email")
            name = data.get("name")
            if not email or not name:
                return Response({"message": "Failed to retrieve required user data from Google."}, status=status.HTTP_404_NOT_FOUND)

            # Check if the user exists or needs to be created
            user, created = Account.objects.get_or_create(email=email)
            if created:
                user.name = name  
                user.username = name  # Ensure username is set
                user.save()

            # Generate token for the user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            if user.is_verified:
                serialized_data = LoginSerializer(user).data
                return Response({
                    "user": serialized_data,
                    "message": "Google Login successful",
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                    "verify": True
                }, status=200)
            else:
                return Response({
                    "message": "Google Login successful. Please enter your mobile number.",
                    "access_token": access_token,
                    "verify": False
                }, status=200)
        else:
            return Response({"message": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)


class RegisterAccountView(APIView):
    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract validated data
        name = serializer.validated_data['name']
        email = serializer.validated_data['email']
        phone = serializer.validated_data['phone']
        
        # Check if account already exists
        account_exists = Account.objects.filter(Q(email=email) | Q(phone=phone)).exists()
        if account_exists:

            return Response({"message": "User already exists with this email or phone"}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user account
        user = Account.objects.create(name=name, email=email, phone=phone, username=name + phone)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Generate OTP
        otp = generate_otp()
        store_otp(phone, otp)
        
        # Send OTP via SMS
        sms_response = send_otp_sms(phone, otp)
        # if not sms_response["success"]:
        #     return Response({"message": "Failed to send OTP.", "error": sms_response["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return response after account creation and OTP sending
        return Response(
            {"message": "Account created successfully. OTP sent to your phone.", "otp":otp, "access_token": access_token},
            status=status.HTTP_201_CREATED
        )

  

class LoginView(APIView):
    def post(self, request):
        serializer = VarifyNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        user = Account.objects.filter(phone=phone).first()
        if not user:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        otp = generate_otp()
        store_otp(phone, otp)
        sms_response = send_otp_sms(phone, otp)
        # if not sms_response["success"]:
        #     return Response({"message": "Failed to send OTP.", "error": sms_response["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "message": "OTP sent successfully",
            "access_token": access_token,
            "otp":otp
        }, status=status.HTTP_200_OK)

class AccountGoogleLogin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VarifyNumberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid phone number data."}, status=400)
        
        phone = serializer.validated_data['phone']
        user = request.user

        # Check if the phone exists and if it's verified
        existing_user = Account.objects.filter(phone=phone).exclude(id=user.id).first()

        if existing_user:
            # If the phone number exists and is verified, return error
            if existing_user.is_verified:
                return Response({"message": "This phone number is already associated with another verified account."}, status=status.HTTP_404_NOT_FOUND)

            # If the phone exists but is not verified, send OTP for verification
            otp = generate_otp()
            store_otp(phone, otp)
            sms_response = send_otp_sms(phone, otp)
            if not sms_response["success"]:
                return Response({"message": "Failed to send OTP.", "error": sms_response["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "OTP sent successfully for phone verification."}, status=200)

        # If the phone doesn't exist, send OTP for the new phone number
        otp = generate_otp()
        store_otp(phone, otp)
        sms_response = send_otp_sms(phone, otp)
        # if not sms_response["success"]:
        #     return Response({"message": "Failed to send OTP.", "error": sms_response["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update user phone and save
        user.phone = phone
        user.save()

        # Generate access token
        refresh = RefreshToken.for_user(user)
 
        return Response({
            "message": "OTP sent successfully for phone verification.",
            "access_token": str(refresh.access_token),
            "otp":otp
        }, status=200)
    
class SendOTPCode(APIView):
    """API to send OTP to user's phone."""
    def post(self, request):
        serializer = VarifyNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone']

        otp = generate_otp()
        store_otp(phone_number, otp)
        sms_response = send_otp_sms(phone_number, otp)

        if sms_response["success"]:
            return Response({'message': 'OTP sent successfully!'}, status=status.HTTP_200_OK)
        return Response({'message': 'Failed to send OTP.'}, status=status.HTTP_404_NOT_FOUND)

class VerifyOTPCode(APIView):



    """API to verify OTP and authenticate user."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_otp = request.data.get('otp')
        user = request.user

        if not user_otp:
            return Response({"message": "Please enter a valid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        stored_otp_data = get_stored_otp(user.phone)  # Assuming phone_number is stored in the user model

        if not stored_otp_data:
            return Response({'message': 'OTP has expired or is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

        stored_otp = stored_otp_data.get('otp')
        otp_generated_time = stored_otp_data.get('timestamp')

        try:
            otp_generated_time = datetime.datetime.fromisoformat(otp_generated_time).astimezone(IST_TIMEZONE)
        except ValueError:
            return Response({'message': 'Invalid OTP format.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check OTP expiration
        expiration_time = otp_generated_time + datetime.timedelta(minutes=OTP_EXPIRATION_MINUTES)
        current_time = timezone.now().astimezone(IST_TIMEZONE)

        if current_time > expiration_time:
            return Response({'message': 'OTP has expired. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        # Compare OTP
        if str(user_otp) == stored_otp:
            cache.delete(f'otp:{user.phone}') 

            if not user.is_verified:
                user.is_verified = True  # Mark user as verified if they were not verified already
                user.save()

            serializer = LoginSerializer(user).data
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'message': 'OTP verified successfully!',
                "data": serializer,
                "access_token": access_token,
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        return Response({'message': 'Invalid OTP!'}, status=status.HTTP_400_BAD_REQUEST)
    


class CreateUserAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        """
        Create a new user address.
        """
        data = request.data
        user= request.user
        print(user)
        # Serialize the data
        serializer = UserAddressSerializer(data=data)
        
        # Validate and save the data
        if serializer.is_valid():
            try:
                data =serializer.save()
                return Response({"message": "Address created successfully.","data":serializer.data}, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    

class UserAddressViewSet(viewsets.ModelViewSet):

    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def get_queryset(self):
        """Filter addresses to only return those belonging to the logged-in user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Assign the logged-in user to the address before saving."""
        serializer.save(user=self.request.user)


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    def get (self, request):
        user = request.user.uid
        try:
            user_details = Account.objects.filter(uid=user).prefetch_related("addresses",'orders')
            if user_details.exists():
                serializer = UserDetailSerializer(user_details.first())

                return Response({"data":serializer.data}, status=status.HTTP_200_OK)
            return Response({'message':"User Not  Found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response ({"message":e},status=status.HTTP_400_BAD_REQUEST)