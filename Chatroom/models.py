from django.db import models
from Core.models import User, Team, Document

# class Team(models.Model):
#     name = models.CharField(max_length=200)
#     members = models.ManyToManyField(User, through='TeamMembership')
#
#
# class TeamMembership(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)
#     date_joined = models.DateTimeField(auto_now_add=True)

class ChatGroup(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # 每个团队有一个公开聊天群
    name = models.CharField(max_length=200)
    is_defalut_chatgroup = models.BooleanField(default=True)
    group_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managed_groups", null=True, blank=True)
    members = models.ManyToManyField(User, through='ChatGroupMembership', related_name="chat_groups",null=True, blank=True)
    is_disbanded = models.BooleanField(default=False) #是否被解散

class ChatGroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'chat_group']

# class EditingMembers(models.Model):
#     document = models.OneToOneField(Document,on_delete=models.CASCADE)
#     members = models.ManyToManyField(User, through='EditingMembership')

# class EditingMembership(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     editing_members = models.ForeignKey(EditingMembers, on_delete=models.CASCADE)
#     date_joined = models.DateTimeField(auto_now_add=True)


class EditMessage(models.Model):
    content = models.TextField()
    cursor_position = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE,null=True)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_at = models.BooleanField(default=False) # 是否是@消息

class DirectMessage(models.Model):
    TEXT = 'text'
    IMAGE = 'image'
    FILE = 'file'
    MESSAGE_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
        (FILE, 'File'),
    ]
    sender = models.ForeignKey(User, related_name="sent_direct_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_direct_messages", on_delete=models.CASCADE)
    # content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=5, choices=MESSAGE_TYPE_CHOICES, default=TEXT)
    # role =

    # 对于文本消息
    content = models.TextField(null=True, blank=True)

    # 对于图片
    image = models.ImageField(upload_to='chat/images/', null=True, blank=True)  # upload_to 定义了上传的路径

    # 对于文件
    file = models.FileField(upload_to='chat/files/', null=True, blank=True)

