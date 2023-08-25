from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from . import consumers
from django.urls import re_path

# websocket_urlpatterns = [...]: 这里定义了一个名为websocket_urlpatterns的列表，其中包含了所有WebSocket连接的URL模式与消费者之间的映射。
# path('ws/chat/<int:team_id>/', consumers.ChatConsumer.as_asgi()): 这是一个WebSocket连接的URL模式定义。让我分解它：
# 'ws/chat/<int:team_id>/': 这是WebSocket的URL一部分，其中<int:team_id>是一个路径参数，表示一个整数值。例如，如果客户端要连接到类似ws://example.com/ws/chat/1/这样的WebSocket地址，那么team_id将被解析为整数1。
# consumers.ChatConsumer.as_asgi(): 这里将名为ChatConsumer的消费者类转换为ASGI（异步服务器网关接口）应用程序，以便在Channels中处理WebSocket连接。.as_asgi()方法是Channels 3+中将消费者转换为ASGI应用程序的方法。
# re_path(r'ws/direct_chat/(?P<receiver_user_id>\d+)/$', consumers.DirectChatConsumer.as_asgi()): 这是另一个WebSocket连接的URL模式定义，使用了re_path来支持正则表达式匹配。让我解释它：
# r'ws/direct_chat/(?P<receiver_user_id>\d+)/$': 这是另一个WebSocket的URL一部分，其中(?P<receiver_user_id>\d+)是一个命名捕获组，用于从URL中提取receiver_user_id作为接收者的用户ID。例如，ws://example.com/ws/direct_chat/2/将提取出receiver_user_id为2。
# consumers.DirectChatConsumer.as_asgi(): 类似上面的模式，这里将名为DirectChatConsumer的消费者类转换为ASGI应用程序，以处理WebSocket连接。

websocket_urlpatterns = [
    path('ws/chat/<int:team_id>/', consumers.ChatConsumer.as_asgi()),  # 注意使用.as_asgi()（针对Channels 3+）
    re_path(r'ws/direct_chat/(?P<receiver_user_id>\d+)/$', consumers.DirectChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),

})
