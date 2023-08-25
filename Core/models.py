from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import *  
from django.contrib.auth.validators import UnicodeUsernameValidator

role_choices = [
    ('Creater','Creater'),
    ('Administrator','Administrator'),
    ('Viewer','Viewer'),
]
permission_choices = [
    ('r','Read_only'),
    ('w','Write_only'),
    ('rw','Read_and_Write'),
]

class User(AbstractUser):
    phone_number = models.CharField(max_length=11, null=True, blank=True)


class Canvas(models.Model):
    pass

class Team(models.Model):
    users = models.ManyToManyField(User, through='TeamMembership')
    # viewer_permission = models.CharField(max_length=100,choices=permission_choices,blank=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    

class Task(models.Model):
    # users = models.ManyToManyField(User, through='UserTask')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team',blank=True,null=True)
    task_permission = models.CharField(max_length=100,choices=permission_choices,blank=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    start_time = models.DateTimeField(blank=True,null=True)
    end_time = models.DateTimeField(blank=True,null=True)
    status = models.CharField(max_length=100)
    canvas = models.ForeignKey(Canvas, on_delete=models.CASCADE, related_name='canvas',blank=True,null=True)

class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=100,choices=role_choices,blank=True)
    permission = models.CharField(choices=permission_choices, max_length=100,blank=True)



