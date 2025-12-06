import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer


class YjsSyncConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Yjs document synchronization.
    Handles JSON messages with base64-encoded Yjs updates.
    """
    
    room_group_name = "collab_room"  # Single global room
    # Store the document state in memory (shared across all connections)
    document_state = None
    # Store cursor states for all connected users
    cursor_states = {}
    
    async def connect(self):
        # Join the global room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Client connected: {self.channel_name}")
    
    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Remove cursor state for this connection and broadcast removal
        client_id = getattr(self, 'client_id', None)
        if client_id and client_id in YjsSyncConsumer.cursor_states:
            del YjsSyncConsumer.cursor_states[client_id]
            # Broadcast cursor removal to all clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "cursor_update",
                    "clientId": client_id,
                    "cursor": None,  # None indicates removal
                    "sender_channel": self.channel_name,
                }
            )
        print(f"Client disconnected: {self.channel_name}")
    
    async def receive(self, text_data=None, bytes_data=None):
        """
        Receive message from WebSocket.
        """
        if text_data:
            try:
                message = json.loads(text_data)
                msg_type = message.get('type')
                
                if msg_type == 'yjs-update':
                    # Store the latest state
                    YjsSyncConsumer.document_state = message.get('data')
                    
                    # Broadcast the Yjs update to all clients in the room
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "yjs_update",
                            "data": message.get('data'),
                            "sender_channel": self.channel_name,
                        }
                    )
                elif msg_type == 'sync-request':
                    # Send current state to the requesting client
                    if YjsSyncConsumer.document_state:
                        await self.send(text_data=json.dumps({
                            "type": "yjs-state",
                            "data": YjsSyncConsumer.document_state
                        }))
                elif msg_type == 'awareness':
                    # Broadcast awareness (typing indicator) to all other clients
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "awareness_update",
                            "clientId": message.get('clientId'),
                            "state": message.get('state'),
                            "sender_channel": self.channel_name,
                        }
                    )
                elif msg_type == 'cursor':
                    # Store and broadcast cursor position
                    client_id = message.get('clientId')
                    self.client_id = client_id  # Store for disconnect handling
                    cursor_data = {
                        'name': message.get('name'),
                        'color': message.get('color'),
                        'position': message.get('position'),
                        'selection': message.get('selection'),
                    }
                    YjsSyncConsumer.cursor_states[client_id] = cursor_data
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "cursor_update",
                            "clientId": client_id,
                            "cursor": cursor_data,
                            "sender_channel": self.channel_name,
                        }
                    )
                elif msg_type == 'cursor-sync-request':
                    # Send all current cursor states to the requesting client
                    await self.send(text_data=json.dumps({
                        "type": "cursor-sync",
                        "cursors": YjsSyncConsumer.cursor_states
                    }))
            except json.JSONDecodeError:
                print("Invalid JSON received")
    
    async def yjs_update(self, event):
        """
        Receive Yjs update from room group.
        Send to WebSocket (but not back to sender).
        """
        if event.get("sender_channel") != self.channel_name:
            await self.send(text_data=json.dumps({
                "type": "yjs-update",
                "data": event["data"]
            }))
    
    async def awareness_update(self, event):
        """
        Receive awareness update from room group.
        Send to WebSocket (but not back to sender).
        """
        if event.get("sender_channel") != self.channel_name:
            await self.send(text_data=json.dumps({
                "type": "awareness",
                "clientId": event.get("clientId"),
                "state": event["state"]
            }))
    
    async def cursor_update(self, event):
        """
        Receive cursor update from room group.
        Send to WebSocket (but not back to sender).
        """
        if event.get("sender_channel") != self.channel_name:
            await self.send(text_data=json.dumps({
                "type": "cursor",
                "clientId": event.get("clientId"),
                "cursor": event.get("cursor")
            }))
