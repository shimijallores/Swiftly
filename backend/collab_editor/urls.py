from django.urls import path
from . import views

urlpatterns = [
    # Auth endpoints
    path('api/auth/register/', views.register_view, name='register'),
    path('api/auth/login/', views.login_view, name='login'),
    path('api/auth/logout/', views.logout_view, name='logout'),
    path('api/auth/me/', views.me_view, name='me'),
    
    # CollabUser endpoints
    path('api/user/', views.get_or_create_user, name='get_or_create_user'),
    path('api/user/<str:client_id>/', views.update_user, name='update_user'),
    
    # Virtual file system endpoints
    path('api/files/', views.file_tree_view, name='file_tree'),
    path('api/files/content/', views.file_content_view, name='file_content'),
    path('api/files/create/', views.file_create_view, name='file_create'),
    path('api/files/upload/', views.file_upload_view, name='file_upload'),
    path('api/files/<uuid:file_id>/', views.file_update_view, name='file_update'),
    path('api/files/<uuid:file_id>/rename/', views.file_rename_view, name='file_rename'),
    path('api/files/<uuid:file_id>/delete/', views.file_delete_view, name='file_delete'),
    path('api/files/<uuid:file_id>/move/', views.file_move_view, name='file_move'),
    
    # Version history endpoints
    path('api/files/<uuid:file_id>/snapshots/', views.file_snapshots_view, name='file_snapshots'),
    path('api/files/<uuid:file_id>/auto-snapshot/', views.auto_snapshot_view, name='auto_snapshot'),
    path('api/snapshots/<uuid:snapshot_id>/', views.snapshot_detail_view, name='snapshot_detail'),
    path('api/snapshots/<uuid:snapshot_id>/restore/', views.snapshot_restore_view, name='snapshot_restore'),
    
    # Room endpoints
    path('api/rooms/', views.rooms_view, name='rooms'),
    path('api/rooms/join/', views.room_join_view, name='room_join'),
    path('api/rooms/<uuid:room_id>/', views.room_detail_view, name='room_detail'),
    path('api/rooms/<uuid:room_id>/leave/', views.room_leave_view, name='room_leave'),
    path('api/rooms/<uuid:room_id>/members/<uuid:member_id>/role/', views.room_member_role_view, name='room_member_role'),
    path('api/rooms/<uuid:room_id>/members/<uuid:member_id>/kick/', views.room_member_kick_view, name='room_member_kick'),
]
