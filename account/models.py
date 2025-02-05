from django.db import models
from django.contrib.auth.models import AbstractUser
from core.utils import UUIDMixin
from django.utils import timezone

# Create your models here.
def upload_location(instance, filename):
    """Generate dynamic upload path for media files."""
    ext = filename.split(".")[-1]
    model_name = instance.__class__.__name__.lower()
class Account(AbstractUser, UUIDMixin):
    userGender = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    username = models.CharField(max_length=200, null=True,blank=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(verbose_name="email", unique=True, blank=True, null=True, max_length=60, default=None)
    profile=models.ImageField(upload_to=upload_location, null=True,blank=True)
    gender=models.CharField(choices=userGender,max_length=20, null=True, blank=True, help_text="Select User Gender")
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ["email", "name",'username']

    def __str__(self) -> str:
        return self.name or "Unknow Name"
    
    


class UserAddress(UUIDMixin):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="addresses")
    country = models.CharField(max_length=100,blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100 ,blank=True, null=True)
    post= models.CharField(max_length=200, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, verbose_name="Address Line 1")
    city = models.CharField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False,blank=True, null=True)

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"

    def __str__(self) -> str:
        return f"{self.address_line_1}, {self.city}, {self.state}, {self.country}"
