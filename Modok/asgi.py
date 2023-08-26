import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Modok.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
import Chatroom.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            Chatroom.routing.websocket_urlpatterns
        )
    )
})