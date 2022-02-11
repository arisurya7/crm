from django.db import models

# Create your models here.
class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    last_active = models.DateField(default=None, blank=True, null=True)
    email = models.EmailField()
    orders = models.IntegerField()
    total_spend = models.IntegerField()
    aov = models.IntegerField(default=None, blank=True, null=True)
    country = models.CharField(max_length=50, default=None, blank=True, null=True)
    city = models.CharField(max_length=50, default=None, blank=True, null=True)
    region = models.CharField(max_length=50, default=None, blank=True, null=True)

class Order(models.Model):
    id_order = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    date = models.DateField()
    status = models.CharField(max_length=50)
    total = models.IntegerField()

class WeightRFM(models.Model):
    id = models.AutoField(primary_key=True)
    w_recency = models.FloatField()
    w_frequency = models.FloatField()
    w_monetary = models.FloatField()
    score_input = models.TextField(default=None, blank=True, null=True)

class WeightLRFM(models.Model):
    id = models.AutoField(primary_key=True)
    w_length = models.FloatField()
    w_recency = models.FloatField()
    w_frequency = models.FloatField()
    w_monetary = models.FloatField()
    score_input = models.TextField(default=None, blank=True, null=True)