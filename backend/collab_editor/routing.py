from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Match UUID format (with hyphens) or simple alphanumeric room IDs
    re_path(r'ws/collab/(?P<room_id>[a-zA-Z0-9-]+)/$', consumers.YjsSyncConsumer.as_asgi()),
    # Keep legacy route for backwards compatibility
    re_path(r'ws/collab/$', consumers.YjsSyncConsumer.as_asgi()),
]
