from django.db import models

# Create your models here.

class Ingridient(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    price = models.IntegerField(null=True,blank=True)
    calories = models.CharField(max_length=250, null=True, blank=True)
    weight = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="media")

    class Meta:
        db_table = 'salad_ingredient'

    def __str__(self):
        return self.name
