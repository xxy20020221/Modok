from django.db import models
from Core.models import Task,User
permission_choices = [
    ('r','Read_only'),
    ('w','Write_only'),
    ('rw','Read_and_Write'),
]
class Design(models.Model):
    # users = models.ManyToManyField(User, through='UserTask')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='design_task',blank=True,null=True)
    task_permission = models.CharField(max_length=100,choices=permission_choices,blank=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    priority = models.IntegerField(blank=True,default=1)
    created_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(blank=True,null=True)
    creater = models.ForeignKey(User,on_delete=models.CASCADE,related_name='design_creater',blank=True,null=True)
    last_editor = models.ForeignKey(User,on_delete=models.CASCADE,related_name='design_last_editor',blank=True,null=True)
    is_shared = models.BooleanField(default=False)


# Create your models here.
class Page(models.Model):
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='pages')
    name = models.CharField(max_length=200)
    background_color = models.CharField(max_length=7, default='#FFFFFF')  # 默认为白色
    image = models.ImageField(upload_to='interfaceDesign/page_images/',null=True)  # 保存铅笔轨迹的图片
    width = models.IntegerField()
    height = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class Component(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='components')
    component_type = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    x_position = models.IntegerField()  # X轴位置
    y_position = models.IntegerField()  # Y轴位置
    width = models.IntegerField()
    height = models.IntegerField()
