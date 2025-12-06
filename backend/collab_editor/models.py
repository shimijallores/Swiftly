from django.db import models
import random
import uuid


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


class VirtualFile(models.Model):
    """
    Virtual filesystem stored in database.
    Each file/folder belongs to a room (project).
    """
    FILE = 'file'
    FOLDER = 'folder'
    TYPE_CHOICES = [
        (FILE, 'File'),
        (FOLDER, 'Folder'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_id = models.CharField(max_length=100, db_index=True, default='default')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=FILE)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    content = models.TextField(blank=True, default='')  # Only for files
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Virtual File"
        verbose_name_plural = "Virtual Files"
        # Prevent duplicate names in the same folder
        unique_together = ['room_id', 'parent', 'name']
        ordering = ['type', 'name']  # Folders first, then alphabetically

    def __str__(self):
        return f"{self.name} ({'📁' if self.type == self.FOLDER else '📄'})"

    @property
    def path(self):
        """Get full path from root."""
        if self.parent:
            return f"{self.parent.path}/{self.name}"
        return self.name

    def to_dict(self, include_children=False):
        """Convert to dictionary for JSON serialization."""
        data = {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'path': self.path,
            'parentId': str(self.parent.id) if self.parent else None,
        }
        if self.type == self.FILE:
            data['updatedAt'] = self.updated_at.isoformat()
        if include_children and self.type == self.FOLDER:
            data['children'] = [
                child.to_dict(include_children=True) 
                for child in self.children.all().order_by('type', 'name')
            ]
        return data

    @classmethod
    def get_tree(cls, room_id='default'):
        """Get full file tree for a room."""
        roots = cls.objects.filter(room_id=room_id, parent=None).order_by('type', 'name')
        return [root.to_dict(include_children=True) for root in roots]

    @classmethod
    def create_default_structure(cls, room_id='default'):
        """Create a default project structure for a new room."""
        # Check if room already has files
        if cls.objects.filter(room_id=room_id).exists():
            return
        
        # Create default structure
        src = cls.objects.create(room_id=room_id, name='src', type=cls.FOLDER)
        cls.objects.create(
            room_id=room_id, 
            name='main.js', 
            type=cls.FILE, 
            parent=src,
            content='// Welcome to Swiftly!\nconsole.log("Hello, World!");\n'
        )
        cls.objects.create(
            room_id=room_id, 
            name='README.md', 
            type=cls.FILE,
            content='# My Project\n\nWelcome to your collaborative project!\n'
        )


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
