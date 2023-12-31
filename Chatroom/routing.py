from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:group_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/live_editing/<int:document_id>/', consumers.LiveEditingConsumer.as_asgi()),
    re_path(r'ws/direct_chat/(?P<receiver_user_id>\d+)/$', consumers.DirectChatConsumer.as_asgi()),
]
