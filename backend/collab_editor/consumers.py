import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Document


class YjsSyncConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Yjs document synchronization.
    Handles JSON messages with base64-encoded Yjs updates.
    Supports room-based isolation.
    """
    
    # Store Yjs updates per room+file (shared across all connections)
    # Key: "room_id:file_id" -> list of base64 encoded updates
    file_updates = {}
    # Store cursor states for all connected users (includes file info)
    cursor_states = {}
    # Max updates to store before requesting compaction
    MAX_UPDATES = 100
    
    @database_sync_to_async
    def load_document_updates(self, room_id='default'):
        """Load document updates from database."""
        doc = Document.get_or_create_document(room_id)
        if doc.yjs_state:
            # The stored state is a JSON array of base64 updates
            try:
                return json.loads(doc.yjs_state.decode('utf-8'))
            except:
                # Legacy: single update stored
                return [base64.b64encode(doc.yjs_state).decode('utf-8')]
        return []
    
    @database_sync_to_async
    def save_document_updates(self, updates_list, room_id='default'):
        """Save all document updates to database."""
        try:
            doc = Document.get_or_create_document(room_id)
            # Store as JSON array of base64 updates
            doc.yjs_state = json.dumps(updates_list).encode('utf-8')
            doc.save(update_fields=['yjs_state', 'updated_at'])
            print(f"Document saved to DB for room {room_id}, {len(updates_list)} updates")
        except Exception as e:
            print(f"Error saving document: {e}")
    
    async def connect(self):
        # Get room_id from URL path, default to 'default'
        self.room_id = self.scope['url_route']['kwargs'].get('room_id', 'default')
        self.room_group_name = f"collab_room_{self.room_id}"
        
        # Join the room-specific group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Client connected to room {self.room_id}: {self.channel_name}")
    
    async def disconnect(self, close_code):
        # Remove cursor state for this connection and broadcast removal BEFORE leaving group
        client_id = getattr(self, 'client_id', None)
        if client_id and client_id in YjsSyncConsumer.cursor_states:
            del YjsSyncConsumer.cursor_states[client_id]
            # Broadcast cursor removal to all clients in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "cursor_update",
                    "clientId": client_id,
                    "cursor": None,  # None indicates removal
                    "sender_channel": self.channel_name,
                }
            )
        
        # Leave the room group AFTER broadcasting
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Client disconnected from room {self.room_id}: {self.channel_name}")
    
    async def receive(self, text_data=None, bytes_data=None):
        """
        Receive message from WebSocket.
        """
        if text_data:
            try:
                message = json.loads(text_data)
                msg_type = message.get('type')
                
                if msg_type == 'yjs-update':
                    # Store update for this room+file
                    update_data = message.get('data')
                    file_id = message.get('fileId')
                    
                    if file_id:
                        # Use room_id:file_id as key to isolate updates per room
                        update_key = f"{self.room_id}:{file_id}"
                        if update_key not in YjsSyncConsumer.file_updates:
                            YjsSyncConsumer.file_updates[update_key] = []
                        YjsSyncConsumer.file_updates[update_key].append(update_data)
                        
                        # Limit stored updates to prevent memory issues
                        if len(YjsSyncConsumer.file_updates[update_key]) > YjsSyncConsumer.MAX_UPDATES:
                            # Keep only the last half of updates
                            YjsSyncConsumer.file_updates[update_key] = YjsSyncConsumer.file_updates[update_key][-50:]
                    
                    # Broadcast the Yjs update to all clients in the room (with fileId)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "yjs_update",
                            "data": update_data,
                            "fileId": file_id,
                            "sender_channel": self.channel_name,
                        }
                    )
                elif msg_type == 'sync-request':
                    # Sync requests are now per-file, handled on frontend
                    pass
                elif msg_type == 'file-sync-request':
                    # Send stored updates for a specific file in this room
                    file_id = message.get('fileId')
                    update_key = f"{self.room_id}:{file_id}"
                    has_updates = file_id and update_key in YjsSyncConsumer.file_updates and len(YjsSyncConsumer.file_updates[update_key]) > 0
                    
                    if has_updates:
                        # Send all stored updates
                        for update in YjsSyncConsumer.file_updates[update_key]:
                            await self.send(text_data=json.dumps({
                                "type": "yjs-state",
                                "fileId": file_id,
                                "data": update
                            }))
                    
                    # Always send sync-complete so client knows whether to init from DB
                    await self.send(text_data=json.dumps({
                        "type": "file-sync-complete",
                        "fileId": file_id,
                        "hasUpdates": has_updates
                    }))
                elif msg_type == 'file-change':
                    # Broadcast file change to all other clients
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "file_change",
                            "clientId": message.get('clientId'),
                            "fileId": message.get('fileId'),
                            "fileName": message.get('fileName'),
                            "filePath": message.get('filePath'),
                            "sender_channel": self.channel_name,
                        }
                    )
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
                    # Store and broadcast cursor position with file info
                    client_id = message.get('clientId')
                    self.client_id = client_id  # Store for disconnect handling
                    cursor_data = {
                        'name': message.get('name'),
                        'color': message.get('color'),
                        'position': message.get('position'),
                        'selection': message.get('selection'),
                        'fileId': message.get('fileId'),
                        'fileName': message.get('fileName'),
                        'filePath': message.get('filePath'),
                    }
                    YjsSyncConsumer.cursor_states[client_id] = cursor_data
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "cursor_update",
                            "clientId": client_id,
                            "cursor": cursor_data,
                            "fileId": message.get('fileId'),
                            "fileName": message.get('fileName'),
                            "filePath": message.get('filePath'),
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
                "fileId": event.get("fileId"),
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
                "cursor": event.get("cursor"),
                "fileId": event.get("fileId"),
                "fileName": event.get("fileName"),
                "filePath": event.get("filePath"),
            }))

    async def file_change(self, event):
        """
        Receive file change notification from room group.
        Send to WebSocket (but not back to sender).
        """
        if event.get("sender_channel") != self.channel_name:
            await self.send(text_data=json.dumps({
                "type": "file-change",
                "clientId": event.get("clientId"),
                "fileId": event.get("fileId"),
                "fileName": event.get("fileName"),
                "filePath": event.get("filePath"),
            }))
