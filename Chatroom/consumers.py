import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
# import logging
#
# logger = logging.getLogger(__name__)


# 导入模型必须在函数内部导入!!!不能在这里导入!!!!!!!

# 群聊
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.team_id = self.scope['url_route']['kwargs']['team_id']
        self.group_name = "chat_" + str(self.team_id)

        # Extract token from query string
        query_string = self.scope['query_string'].decode('utf-8')
        token_param = [param.split('=') for param in query_string.split('&') if param.startswith('token=')]

        if token_param and len(token_param[0]) > 1:
            token_key = token_param[0][1]
            try:
                token = await database_sync_to_async(Token.objects.get)(key=token_key)
                user = await self.get_user_from_token(token)
                self.scope['user'] = user
            except Token.DoesNotExist:
                self.scope['user'] = AnonymousUser()
                # logger.error(f"Invalid token provided: {token_key}")  # 添加日志记录

        # If user is authenticated, proceed with the connection, else close the connection
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # logger.error(f"WebSocket connection rejected for user: {self.scope['user']}")  # 添加日志记录
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        from Chatroom.models import Message
        text_data_json = json.loads(text_data)

        message_type = text_data_json['type']
        message_content = text_data_json['content']

        if message_type == Message.TEXT:
            message = await self.save_text_message(message_content)
            # 检查是否有@符号
            if '@' in message_content:
                await self.handle_mentions(message_content, message)
        elif message_type == Message.IMAGE:
            message = await self.get_message_by_id(message_content, Message.IMAGE)
        elif message_type == Message.FILE:
            message = await self.get_message_by_id(message_content, Message.FILE)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message_type': message_type,
                'content': message_content,  # This is either text or the ID for file/image.
                'message_id': message.id,
                'username': self.scope['user'].username
            }
        )

    async def handle_mentions(self, content, message):
        from Chatroom.models import Mention
        # 如果@所有用户
        if '@all' in content:
            mention = await self.create_mention(message, None, Mention.ALL_USERS)
            users = await self.get_all_users()
            for user in users:
                await self.send_notification(user, content)
        else:
            # 查找特定的@用户
            users = await self.get_all_users()
            for user in users:
                username = user.username
                if f"@{username}" in content:
                    mention = await self.create_mention(message, user, Mention.SPECIFIC_USER)
                    await self.send_notification(user, content)


    @database_sync_to_async
    def get_message_by_id(self, content_id, message_type):
        from Chatroom.models import Message
        return Message.objects.get(pk=content_id, message_type=message_type)
    async def chat_message(self, event):
        message = event['content']
        message_type = event['message_type']
        username = event['username']
        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'message_type': message_type,
            'content': message,
            'username':username,
        }))

    @database_sync_to_async
    def save_text_message(self, content):
        from Chatroom.models import Message, ChatGroup

        chat_group = ChatGroup.objects.get(team_id=self.team_id)

        return Message.objects.create(
            sender=self.scope["user"],
            content=content,
            group=chat_group,
            message_type=Message.TEXT
        )

    @database_sync_to_async
    def save_image_message(self, content):
        from Chatroom.models import Message, ChatGroup

        chat_group = ChatGroup.objects.get(team_id=self.team_id)

        return Message.objects.create(
            sender=self.scope["user"],
            image=content,
            group=chat_group,
            message_type=Message.IMAGE
        )

    @database_sync_to_async
    def save_file_message(self, content):
        from Chatroom.models import Message, ChatGroup

        chat_group = ChatGroup.objects.get(team_id=self.team_id)

        return Message.objects.create(
            sender=self.scope["user"],
            file=content,
            group=chat_group,
            message_type=Message.FILE
        )

    @database_sync_to_async
    def create_mention(self, message, user, mention_type):
        from Chatroom.models import Mention
        return Mention.objects.create(
            message=message,
            user=user,
            mention_type=mention_type
        )

    @database_sync_to_async
    def get_all_users(self):
        from Core.models import Team
        team = Team.objects.get(pk=self.scope['url_route']['kwargs']['team_id'])
        return team.users.all()

    async def send_notification(self, user, message_content):
        # 使用channel layer广播通知
        await self.create_notification(user, message_content)  # 添加了await
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"notifications_{user.id}",
            {
                'type': 'send_notification',
                'message': {
                    'content': message_content,
                    # 可能还需要包括其他通知的详细信息
                }
            }
        )

    @database_sync_to_async
    def create_notification(self, user, message_content):
        from Chatroom.models import Notification
        return Notification.objects.create(
            user=user,
            message=message_content,
            is_at=True if "@" in message_content else False
        )

    @database_sync_to_async
    def get_user_from_token(self, token):
        return token.user


# 私聊, 为私聊创建了一个特定的group_name，确保两个私聊的用户之间的消息不会被其他用户看到
class DirectChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user_from_token(self, token):
        return token.user
    async def connect(self):
        self.receiver_user_id = self.scope['url_route']['kwargs']['receiver_user_id']

        # Extract token from query string
        query_string = self.scope['query_string'].decode('utf-8')
        token_param = [param.split('=') for param in query_string.split('&') if param.startswith('token=')]

        # If token is present in the query string
        if token_param and len(token_param[0]) > 1:
            token_key = token_param[0][1]

            # Validate the token and retrieve the associated user
            try:
                token = await database_sync_to_async(Token.objects.get)(key=token_key)
                user = await self.get_user_from_token(token)
                self.scope['user'] = user
            except Token.DoesNotExist:
                # If the token does not exist or is invalid, set the user as AnonymousUser
                self.scope['user'] = AnonymousUser()

        # If user is authenticated, proceed with the connection, else close the connection
        if self.scope['user'].is_authenticated:
            # self.group_name = f"dm_{self.scope['user'].id}_{self.receiver_user_id}"  # Construct the group name using the authenticated user's ID
            sender_id = self.scope['user'].id
            receiver_id = int(self.scope['url_route']['kwargs']['receiver_user_id'])

            self.group_name = f"dm_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
            print("jjjjjjjj"+self.group_name)
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from Chatroom.models import Message
        text_data_json = json.loads(text_data)

        message_type = text_data_json['type']
        message_content = text_data_json['content']

        if message_type == Message.TEXT:
            message = await self.save_text_message(message_content)
        elif message_type == Message.IMAGE:
            message = await self.get_message_by_id(message_content, Message.IMAGE)
        elif message_type == Message.FILE:
            message = await self.get_message_by_id(message_content, Message.FILE)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'direct_message',
                'message_type': message_type,
                'content': message_content,  # This can either be text or the ID for file/image.
                'message_id': message.id,
            }
        )

    async def direct_message(self, event):
        message_type = event['message_type']
        content = event['content']

        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'message_type': message_type,
            'content': content,
        }))

    @database_sync_to_async
    def get_message_by_id(self, content_id, message_type):
        from Chatroom.models import DirectMessage
        return DirectMessage.objects.get(pk=content_id, message_type=message_type)

    @database_sync_to_async
    def save_text_message(self, content):
        from Chatroom.models import DirectMessage
        from Core.models import User
        from Chatroom.models import Message
        return DirectMessage.objects.create(
            sender=self.scope["user"],
            receiver=User.objects.get(id=self.receiver_user_id),
            content=content,
            message_type=Message.TEXT
        )

    @database_sync_to_async
    def save_image_message(self, content):
        from Chatroom.models import DirectMessage
        from Core.models import User
        from Chatroom.models import Message
        return DirectMessage.objects.create(
            sender=self.scope["user"],
            receiver=User.objects.get(id=self.receiver_user_id),
            image=content,
            message_type=Message.IMAGE
        )

    @database_sync_to_async
    def save_file_message(self, content):
        from Chatroom.models import DirectMessage
        from Core.models import User
        from Chatroom.models import Message
        return DirectMessage.objects.create(
            sender=self.scope["user"],
            receiver=User.objects.get(id=self.receiver_user_id),
            file=content,
            message_type=Message.FILE
        )


