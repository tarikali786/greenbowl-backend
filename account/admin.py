from django.contrib import admin
from account.models import Account,UserAddress
# Register your models here.

admin.site.register([Account,UserAddress])