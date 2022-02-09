from django.db import models

# Create your models here.
class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    recency = models.IntegerField()
    frequency = models.IntegerField()
    monetary = models.IntegerField()

class WeightRFM(models.Model):
    id = models.AutoField(primary_key=True)
    w_recency = models.FloatField()
    w_frequency = models.FloatField()
    w_monetary = models.FloatField()
    score_input = models.TextField(default=None, blank=True, null=True)