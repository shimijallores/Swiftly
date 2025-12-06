from django.contrib import admin
from .models import Document, CollabUser


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'updated_at', 'created_at', 'has_content')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('room_id',)
    
    def has_content(self, obj):
        return bool(obj.yjs_state)
    has_content.boolean = True
    has_content.short_description = 'Has Content'


@admin.register(CollabUser)
class CollabUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_id', 'color', 'last_seen', 'created_at')
    search_fields = ('name', 'client_id')
    readonly_fields = ('created_at', 'last_seen')
