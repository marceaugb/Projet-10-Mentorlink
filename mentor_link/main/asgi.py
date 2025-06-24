# mentor_link/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import app_mentorlink.routing  # Importez les routes WebSocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentor_link.main.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(app_mentorlink.routing.websocket_urlpatterns)
    ),
})