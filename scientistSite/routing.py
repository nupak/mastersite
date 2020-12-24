from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat.routing import websocket_urls
#from chat.middleware import SimpleMiddlewareStack, MyMiddlewareStack

application = ProtocolTypeRouter({
    "websocket": (
        AllowedHostsOriginValidator(
                URLRouter(
                    websocket_urls
            )
        )
    ),
})