# 定义WebSocket的路由

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:team_id>/', consumers.ChatConsumer.as_asgi()),
]
