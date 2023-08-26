from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:team_id>/', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/direct_chat/(?P<receiver_user_id>\d+)/$', consumers.DirectChatConsumer.as_asgi()),
]
