from django.db import models
from Core.models import Task

# Create your models here.
class Page(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='pages')
    name = models.CharField(max_length=200)
    background_color = models.CharField(max_length=7, default='#FFFFFF')  # 默认为白色
    image = models.ImageField(upload_to='interfaceDesign/page_images/',null=True)  # 保存铅笔轨迹的图片
    width = models.IntegerField()
    height = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

class Component(models.Model):
    COMPONENT_CHOICES = [
        ('button', 'Button'),
        ('textbox', 'Textbox'),

    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='components')
    component_type = models.CharField(max_length=50, choices=COMPONENT_CHOICES)
    name = models.CharField(max_length=200)
    x_position = models.IntegerField()  # X轴位置
    y_position = models.IntegerField()  # Y轴位置
    width = models.IntegerField()
    height = models.IntegerField()
