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
