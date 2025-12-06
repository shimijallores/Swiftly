from django.db import models
import random


class Document(models.Model):
    """
    Stores the Yjs document state for persistence.
    Currently uses a single global document (room_id='default').
    """
    room_id = models.CharField(max_length=100, unique=True, db_index=True, default='default')
    yjs_state = models.BinaryField(null=True, blank=True)  # Store Yjs update as binary
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"Document {self.room_id}"

    @classmethod
    def get_or_create_document(cls, room_id='default'):
        doc, created = cls.objects.get_or_create(room_id=room_id)
        return doc


class CollabUser(models.Model):
    """
    Represents a collaborative editor user with persistent identity.
    """
    client_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7)  # Hex color like #e91e63
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    USER_NAMES = [
        "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", 
        "Grace", "Henry", "Ivy", "Jack", "Kate", "Leo",
        "Mia", "Noah", "Olivia", "Peter", "Quinn", "Ruby"
    ]
    
    USER_COLORS = [
        "#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3",
        "#00bcd4", "#009688", "#4caf50", "#ff9800", "#ff5722"
    ]

    class Meta:
        verbose_name = "Collab User"
        verbose_name_plural = "Collab Users"

    def __str__(self):
        return f"{self.name} ({self.client_id[:8]}...)"

    @classmethod
    def get_or_create_user(cls, client_id):
        """
        Get existing user or create a new one with random name and color.
        """
        user, created = cls.objects.get_or_create(
            client_id=client_id,
            defaults={
                'name': f"{random.choice(cls.USER_NAMES)}{random.randint(1, 99)}",
                'color': random.choice(cls.USER_COLORS),
            }
        )
        if not created:
            # Update last_seen
            user.save(update_fields=['last_seen'])
        return user, created
