import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import Chatroom.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Modok.settings')


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Chatroom.routing.websocket_urlpatterns
        )
    ),
})
