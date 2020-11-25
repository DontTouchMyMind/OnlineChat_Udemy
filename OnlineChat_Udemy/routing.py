from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack

from chat.routing import websocket_urls

application = ProtocolTypeRouter({
    'websocket': SessionMiddlewareStack(
        URLRouter(
            websocket_urls,
        )
    )
})
