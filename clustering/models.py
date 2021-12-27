from django.db import models

# Create your models here.
class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    recency = models.IntegerField()
    frequency = models.IntegerField()
    monetary = models.IntegerField()
