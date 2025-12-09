from django.db import models
from django.contrib.auth.models import User
import random
import uuid
import string
import hashlib


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
        cls.objects.create(
            room_id=room_id, 
            name='main.js', 
            type=cls.FILE, 
            content='// Welcome to Swiftly!\nconsole.log("Hello, World!");\n'
        )
        cls.objects.create(
            room_id=room_id, 
            name='index.html', 
            type=cls.FILE, 
        )
        cls.objects.create(
            room_id=room_id, 
            name='style.css', 
            type=cls.FILE, 
        )
        cls.objects.create(
            room_id=room_id, 
            name='README.md', 
            type=cls.FILE,
            content='# My Project\n\nWelcome to swiftly!\n'
        )

    @classmethod
    def create_template_structure(cls, room_id, template):
        """Create a template-based project structure for a new room."""
        # Check if room already has files
        if cls.objects.filter(room_id=room_id).exists():
            return

        if template == 'vue':
            # Create Vue.js template structure
            cls.objects.create(
                room_id=room_id,
                name='index.html',
                type=cls.FILE,
                content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue.js App</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>
<body>
    <div id="app">
        <div class="min-h-screen bg-gray-100 py-8">
            <div class="max-w-4xl mx-auto px-4">
                <header class="text-center mb-8">
                    <h1 class="text-4xl font-bold text-gray-800 mb-2">{{ title }}</h1>
                    <p class="text-gray-600">{{ message }}</p>
                </header>

                <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                    <h2 class="text-2xl font-semibold mb-4">Counter: {{ count }}</h2>
                    <div class="flex gap-4">
                        <button
                            @click="increment"
                            class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
                            Increment
                        </button>
                        <button
                            @click="decrement"
                            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">
                            Decrement
                        </button>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow-md p-6">
                    <h2 class="text-2xl font-semibold mb-4">Todo List</h2>
                    <div class="mb-4">
                        <input
                            v-model="newTodo"
                            @keyup.enter="addTodo"
                            placeholder="Add a new todo..."
                            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <ul class="space-y-2">
                        <li
                            v-for="(todo, index) in todos"
                            :key="index"
                            class="flex items-center gap-3 p-2 bg-gray-50 rounded">
                            <input
                                type="checkbox"
                                v-model="todo.completed"
                                class="w-4 h-4 text-blue-600">
                            <span :class="{ 'line-through text-gray-500': todo.completed }">
                                {{ todo.text }}
                            </span>
                            <button
                                @click="removeTodo(index)"
                                class="ml-auto text-red-500 hover:text-red-700">
                                ✕
                            </button>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp } = Vue;

        createApp({
            data() {
                return {
                    title: 'Welcome to Vue.js!',
                    message: 'This is a simple Vue.js application with CDN.',
                    count: 0,
                    newTodo: '',
                    todos: [
                        { text: 'Learn Vue.js', completed: false },
                        { text: 'Build something awesome', completed: false }
                    ]
                }
            },
            methods: {
                increment() {
                    this.count++;
                },
                decrement() {
                    this.count--;
                },
                addTodo() {
                    if (this.newTodo.trim()) {
                        this.todos.push({
                            text: this.newTodo.trim(),
                            completed: false
                        });
                        this.newTodo = '';
                    }
                },
                removeTodo(index) {
                    this.todos.splice(index, 1);
                }
            }
        }).mount('#app');
    </script>
</body>
</html>"""
            )

            cls.objects.create(
                room_id=room_id,
                name='README.md',
                type=cls.FILE,
                content="""# Vue.js Template

This is a Vue.js application created with Swiftly.

## Features

- Vue 3 with CDN
- Counter component
- Todo list functionality
- Responsive design with Tailwind CSS

## Getting Started

1. Open `index.html` in your browser
2. Start coding collaboratively!

## Vue.js Documentation

- [Vue.js Guide](https://vuejs.org/guide/introduction.html)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
"""
            )
        else:
            # Fallback to default structure
            cls.create_default_structure(room_id)


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


class Room(models.Model):
    """
    A collaborative room/workspace that users can join.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=8, unique=True, db_index=True)  # Share code
    password_hash = models.CharField(max_length=128)  # Hashed password
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @staticmethod
    def generate_code():
        """Generate a unique 8-character room code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Room.objects.filter(code=code).exists():
                return code

    @staticmethod
    def hash_password(password):
        """Hash a password for storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        """Check if password matches."""
        return self.password_hash == self.hash_password(password)

    def to_dict(self, include_members=False):
        """Convert to dictionary for JSON serialization."""
        data = {
            'id': str(self.id),
            'name': self.name,
            'code': self.code,
            'ownerId': self.owner.id,
            'ownerName': self.owner.username,
            'createdAt': self.created_at.isoformat(),
            'memberCount': self.members.count(),
        }
        if include_members:
            data['members'] = [
                member.to_dict() for member in self.members.all()
            ]
        return data


class RoomMember(models.Model):
    """
    Membership of a user in a room with a specific role.
    """
    OWNER = 'owner'
    EDITOR = 'editor'
    VIEWER = 'viewer'
    ROLE_CHOICES = [
        (OWNER, 'Owner'),
        (EDITOR, 'Editor'),
        (VIEWER, 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=EDITOR)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Room Member"
        verbose_name_plural = "Room Members"
        unique_together = ['room', 'user']
        ordering = ['role', 'joined_at']

    def __str__(self):
        return f"{self.user.username} in {self.room.name} ({self.role})"

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'userId': self.user.id,
            'username': self.user.username,
            'role': self.role,
            'joinedAt': self.joined_at.isoformat(),
        }


class FileSnapshot(models.Model):
    """
    Version history snapshot for a file.
    Stores content snapshots with timestamps and author info.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(VirtualFile, on_delete=models.CASCADE, related_name='snapshots')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    author_name = models.CharField(max_length=100, default='Unknown')  # Cached name in case user is deleted
    created_at = models.DateTimeField(auto_now_add=True)
    # Size in bytes for display
    size = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "File Snapshot"
        verbose_name_plural = "File Snapshots"
        ordering = ['-created_at']  # Most recent first
    
    def __str__(self):
        return f"Snapshot of {self.file.name} at {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Calculate size before saving
        self.size = len(self.content.encode('utf-8'))
        super().save(*args, **kwargs)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'fileId': str(self.file.id),
            'fileName': self.file.name,
            'authorId': self.author.id if self.author else None,
            'authorName': self.author_name,
            'createdAt': self.created_at.isoformat(),
            'size': self.size,
        }
    
    @classmethod
    def create_snapshot(cls, file, user=None):
        """
        Create a new snapshot for a file.
        Returns the created snapshot or None if content unchanged.
        """
        # Get the latest snapshot to compare
        latest = cls.objects.filter(file=file).first()
        
        # Don't create duplicate snapshots if content is identical
        if latest and latest.content == file.content:
            return None
        
        author_name = 'Unknown'
        if user:
            author_name = user.username
        
        return cls.objects.create(
            file=file,
            content=file.content,
            author=user,
            author_name=author_name,
        )
    
    @classmethod
    def cleanup_old_snapshots(cls, file, keep_count=10):
        """
        Keep only the most recent N snapshots for a file.
        Default keeps 10 snapshots.
        """
        snapshots = cls.objects.filter(file=file).order_by('-created_at')
        to_delete = snapshots[keep_count:]
        if to_delete.exists():
            to_delete.delete()
