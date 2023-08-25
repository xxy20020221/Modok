import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from Chatroom.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.team_id = self.scope['url_route']['kwargs']['team_id']
        await self.channel_layer.group_add(
            self.team_id,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.team_id,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        message_type = text_data_json['type']
        message_content = text_data_json['content']

        # 根据消息类型保存消息到数据库
        if message_type == Message.TEXT:
            message = await self.save_text_message(message_content)
        elif message_type == Message.IMAGE:
            # 处理图片内容可能涉及到一些异步文件上传逻辑，这里简化处理
            message = await self.save_image_message(message_content)
        elif message_type == Message.FILE:
            # 同样，处理文件内容可能涉及到异步文件上传逻辑
            message = await self.save_file_message(message_content)

        # 广播消息到群组
        await self.channel_layer.group_send(
            self.team_id,
            {
                'type': 'chat_message',
                'message_type': message_type,
                'content': message_content,
                'message_id': message.id,
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def save_text_message(self, content):
        return Message.objects.create(
            sender=self.scope["user"],
            content=content,
            team_id=self.team_id,
            message_type=Message.TEXT
        )

    @database_sync_to_async
    def save_image_message(self, content):
        # 这里的content可以是图片的URL或者其他方式标识图片的内容
        # 如果是通过WebSocket上传的图片文件，那么处理逻辑会更复杂，需要考虑如何在异步环境中进行文件上传
        return Message.objects.create(
            sender=self.scope["user"],
            image=content,
            team_id=self.team_id,
            message_type=Message.IMAGE
        )

    @database_sync_to_async
    def save_file_message(self, content):
        # 类似于image，content可以是文件的URL或其他标识
        return Message.objects.create(
            sender=self.scope["user"],
            file=content,
            team_id=self.team_id,
            message_type=Message.FILE
        )

