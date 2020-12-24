from django.conf.urls import url
from chat.consumers import ChatConsumer, roomlistConsumer


websocket_urls = [
    url(r'^ws/roomlist/$', roomlistConsumer),
    url(r'^ws/chat/(?P<group_id>\d+)/$', ChatConsumer),
    #url(r'^ws/middleware/$', MyMiddlewareConsumer),
]