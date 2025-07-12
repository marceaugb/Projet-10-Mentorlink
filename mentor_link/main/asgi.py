import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentor_link.main.settings')

# Initialise l'application Django (http)
django_asgi_app = get_asgi_application()

# Import des routes WebSocket APRÈS l'initialisation de Django
import app_mentorlink.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(app_mentorlink.routing.websocket_urlpatterns)
    ),
})

