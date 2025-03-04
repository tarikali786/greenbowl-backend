from django.contrib import admin
from salad.models import * 
# Register your models here.
admin.site.register([Ingredient,Salad,Recipe])