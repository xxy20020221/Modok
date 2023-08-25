from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, through='TeamMembership')



class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)



class ChatGroup(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)  # 每个团队有一个公开聊天群
    name = models.CharField(max_length=200)


class Message(models.Model):
    TEXT = 'text'
    IMAGE = 'image'
    FILE = 'file'
    MESSAGE_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
        (FILE, 'File'),
    ]

    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=5, choices=MESSAGE_TYPE_CHOICES, default=TEXT)
    # role =

    # 对于文本消息
    content = models.TextField(null=True, blank=True)

    # 对于图片
    image = models.ImageField(upload_to='chat/images/', null=True, blank=True)  # upload_to 定义了上传的路径

    # 对于文件
    file = models.FileField(upload_to='chat/files/', null=True, blank=True)


class Mention(models.Model):
    SPECIFIC_USER = 'specific'
    ALL_USERS = 'all'
    MENTION_TYPE_CHOICES = [
        (SPECIFIC_USER, 'Specific User'),
        (ALL_USERS, 'All Users'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # 如果是 "@" 所有人，这可以为空
    mention_type = models.CharField(max_length=10, choices=MENTION_TYPE_CHOICES)


class Notification(models.Model):
    UNREAD = 'unread'
    READ = 'read'
    STATUS_CHOICES = [
        (UNREAD, 'Unread'),
        (READ, 'Read'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default=UNREAD)
    timestamp = models.DateTimeField(auto_now_add=True)

