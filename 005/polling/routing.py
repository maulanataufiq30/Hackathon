# polling/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from sse.consumers import SSEConsumer

application = ProtocolTypeRouter({
    "http": URLRouter([
        path('sse/<uuid:poll_id>/', SSEConsumer.as_asgi()),
    ]),
})