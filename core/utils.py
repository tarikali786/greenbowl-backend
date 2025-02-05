import uuid
from django.db import models
import random
import os
from django.core.cache import cache
from twilio.base.exceptions import TwilioRestException
from django.utils import timezone
from twilio.rest import Client
import pytz
OTP_EXPIRATION_MINUTES = 5

import pytz
class UUIDMixin(models.Model):
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        abstract = True



def generate_otp():
    """Generate a 5-digit OTP."""
    return str(random.randint(10000, 99999))


def store_otp(phone, otp):
    """Store OTP in cache with expiration time."""
    otp_data = {
        "otp": otp,
        "timestamp": timezone.now().isoformat()  # Store in ISO format
    }
    cache.set(f'otp:{phone}', otp_data, timeout=OTP_EXPIRATION_MINUTES * 60)  # Store for 5 minutes


def get_stored_otp(phone):
    """Retrieve stored OTP from cache."""
    return cache.get(f'otp:{phone}')


def send_otp_sms(phone, otp):
    """Send OTP via Twilio SMS."""
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f'Welcome to GreenBowl! Your OTP is {otp}. It is valid for {OTP_EXPIRATION_MINUTES} minutes. Do not share it with anyone.',
            from_=twilio_phone_number,
            to=f"+91{phone}"
        )
        return {"success": True, "message_sid": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}


