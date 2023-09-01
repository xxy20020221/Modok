from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import *  
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
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

document_choices = [
    ('1','Not Started'),
    ('2','In Progress'),
    ('3','Completed'),
]

write_permission_choices = [
    ('1','team'),
    ('2','all'),
]

gender_choices = [
    ('male','male'),
    ('female','female'),
]
class User(AbstractUser):
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    gender = models.CharField(max_length=10,choices=gender_choices,null=True,blank=True)
    description = models.CharField(max_length=1000,null=True,blank=True)
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True)
    register_date = models.DateTimeField(auto_now_add=True)

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
    created_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(blank=True,null=True)
    is_shared = models.BooleanField(default=False)

class Canvas(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='canvastask',blank=True,null=True)


class Directory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='directories')
    dir_name = models.CharField(max_length=100)
    dir_path = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    creater = models.ForeignKey(User,on_delete=models.CASCADE,related_name='dir_creater',blank=True,null=True)
    last_editor = models.ForeignKey(User,on_delete=models.CASCADE,related_name='dir_last_editor',blank=True,null=True)

#这里先假设一个task可以对应多个document
class Document(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='documenttask',blank=True,null=True)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    document_path = models.CharField(max_length=100,blank=True)
    document_name = models.CharField(max_length=100,blank=True)
    content = models.CharField(max_length=1000,blank=True,null=True)
    priority = models.IntegerField(blank=True,default=1)
    status = models.CharField(max_length=100,choices=document_choices,blank=True)
    expiration_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    creater = models.ForeignKey(User,on_delete=models.CASCADE,related_name='creater',blank=True,null=True)
    last_editor = models.ForeignKey(User,on_delete=models.CASCADE,related_name='last_editor',blank=True,null=True)
    write_permission = models.CharField(max_length=100,choices=write_permission_choices,default='1')
    write_code = models.CharField(max_length=100,blank=True,null=True)
    read_code = models.CharField(max_length=100,blank=True,null=True)


class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=100,choices=role_choices,blank=True)
    permission = models.CharField(choices=permission_choices, max_length=100,blank=True)



