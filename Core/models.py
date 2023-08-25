from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import *  
from django.contrib.auth.validators import UnicodeUsernameValidator

class User(AbstractUser):
    phone_number = models.CharField(max_length=11, null=True, blank=True)

class Canvas(models.Model):
    pass

class Task(models.Model):
    administrator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    collaborator = models.ForeignKey(User, on_delete=models.CASCADE,related_name='collaborator')
    viewer = models.ForeignKey(User, on_delete=models.CASCADE,related_name='viewer')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=100)
    canvas = models.ForeignKey(Canvas, on_delete=models.CASCADE, related_name='canvas')


