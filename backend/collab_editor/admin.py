from django.contrib import admin
from django.utils.html import format_html
from .models import Document, CollabUser, VirtualFile, Room, RoomMember, FileSnapshot


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'updated_at', 'created_at', 'has_content')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('room_id',)
    list_filter = ('created_at', 'updated_at')
    
    def has_content(self, obj):
        return bool(obj.yjs_state)
    has_content.boolean = True
    has_content.short_description = 'Has Content'


@admin.register(CollabUser)
class CollabUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_id', 'color_display', 'last_seen', 'created_at')
    search_fields = ('name', 'client_id')
    readonly_fields = ('created_at', 'last_seen')
    list_filter = ('created_at', 'last_seen')
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'


@admin.register(VirtualFile)
class VirtualFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'room_id', 'parent', 'path', 'updated_at')
    list_filter = ('type', 'room_id', 'created_at')
    search_fields = ('name', 'room_id')
    readonly_fields = ('id', 'path', 'created_at', 'updated_at')
    raw_id_fields = ('parent',)
    ordering = ('room_id', 'type', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'type', 'room_id', 'parent')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


class RoomMemberInline(admin.TabularInline):
    model = RoomMember
    extra = 0
    readonly_fields = ('id', 'joined_at')
    raw_id_fields = ('user',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'owner', 'member_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'code', 'owner__username')
    readonly_fields = ('id', 'code', 'created_at', 'updated_at')
    raw_id_fields = ('owner',)
    inlines = [RoomMemberInline]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'code', 'owner')
        }),
        ('Security', {
            'fields': ('password_hash',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__username', 'room__name', 'room__code')
    readonly_fields = ('id', 'joined_at')
    raw_id_fields = ('room', 'user')


@admin.register(FileSnapshot)
class FileSnapshotAdmin(admin.ModelAdmin):
    list_display = ('file', 'author_name', 'size_display', 'created_at')
    list_filter = ('created_at', 'author_name')
    search_fields = ('file__name', 'author_name')
    readonly_fields = ('id', 'size', 'created_at')
    raw_id_fields = ('file', 'author')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('id', 'file', 'author', 'author_name')
        }),
        ('Content', {
            'fields': ('content', 'size'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )
    
    def size_display(self, obj):
        if obj.size < 1024:
            return f"{obj.size} B"
        elif obj.size < 1024 * 1024:
            return f"{obj.size / 1024:.1f} KB"
        return f"{obj.size / (1024 * 1024):.1f} MB"
    size_display.short_description = 'Size'
