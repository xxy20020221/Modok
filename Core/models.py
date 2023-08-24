from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import *  

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    credits = models.IntegerField(default=100)
    travel_num = models.IntegerField(default=0)
    user_nickname = models.CharField(max_length=200, default=None)
    last_recover_date = models.DateField(null=True,blank=True)