from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import json

from .models import CollabUser, VirtualFile


# ============ Auth Views ============

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    """
    Register a new user.
    POST body: { "username": "john", "email": "john@example.com", "password": "secret123" }
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email', '')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create associated CollabUser with username as client_id
        collab_user, _ = CollabUser.get_or_create_user(str(user.id))
        collab_user.name = username
        collab_user.save()
        
        # Log in the user
        login(request, user)
        
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'collab_user': {
                'name': collab_user.name,
                'color': collab_user.color,
            }
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """
    Log in a user.
    POST body: { "username": "john", "password": "secret123" }
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Get or create CollabuUser
            collab_user, _ = CollabUser.get_or_create_user(str(user.id))
            if collab_user.name != username:
                collab_user.name = username
                collab_user.save()
            
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'collab_user': {
                    'client_id': collab_user.client_id,
                    'name': collab_user.name,
                    'color': collab_user.color,
                }
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """Log out the current user."""
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})


@require_http_methods(["GET"])
def me_view(request):
    """Get current authenticated user info."""
    if request.user.is_authenticated:
        collab_user, _ = CollabUser.get_or_create_user(str(request.user.id))
        return JsonResponse({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'collab_user': {
                'client_id': collab_user.client_id,
                'name': collab_user.name,
                'color': collab_user.color,
            }
        })
    else:
        return JsonResponse({'error': 'Not authenticated'}, status=401)


# ============ CollabUser Views ============

@csrf_exempt
@require_http_methods(["POST"])
def get_or_create_user(request):
    """
    Get or create a user based on client_id.
    POST body: { "client_id": "abc123" }
    Returns: { "client_id": "abc123", "name": "Alice42", "color": "#e91e63", "created": true }
    """
    try:
        data = json.loads(request.body)
        client_id = data.get('client_id')
        
        if not client_id:
            return JsonResponse({'error': 'client_id is required'}, status=400)
        
        user, created = CollabUser.get_or_create_user(client_id)
        
        return JsonResponse({
            'client_id': user.client_id,
            'name': user.name,
            'color': user.color,
            'created': created,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["PUT"])
def update_user(request, client_id):
    """
    Update user's name or color.
    PUT body: { "name": "NewName", "color": "#ff5722" }
    """
    try:
        user = CollabUser.objects.get(client_id=client_id)
        data = json.loads(request.body)
        
        if 'name' in data:
            user.name = data['name']
        if 'color' in data:
            user.color = data['color']
        
        user.save()
        
        return JsonResponse({
            'client_id': user.client_id,
            'name': user.name,
            'color': user.color,
        })
    except CollabUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


# ============ Virtual File System Views ============

@require_http_methods(["GET"])
def file_tree_view(request):
    """
    Get the virtual file tree for a room.
    Query param: room_id (defaults to 'default')
    """
    room_id = request.GET.get('room_id', 'default')
    
    # Create default structure if room is empty
    VirtualFile.create_default_structure(room_id)
    
    tree = VirtualFile.get_tree(room_id)
    return JsonResponse({'tree': tree})


@csrf_exempt
@require_http_methods(["GET"])
def file_content_view(request):
    """
    Get the content of a virtual file.
    Query param: id (file UUID)
    """
    file_id = request.GET.get('id')
    
    if not file_id:
        return JsonResponse({'error': 'File ID is required'}, status=400)
    
    try:
        file = VirtualFile.objects.get(id=file_id, type=VirtualFile.FILE)
        return JsonResponse({
            'id': str(file.id),
            'name': file.name,
            'path': file.path,
            'content': file.content,
        })
    except VirtualFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def file_create_view(request):
    """
    Create a new file or folder.
    POST body: { "room_id": "default", "name": "app.js", "type": "file", "parentId": null, "content": "" }
    """
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id', 'default')
        name = data.get('name')
        file_type = data.get('type', VirtualFile.FILE)
        parent_id = data.get('parentId')
        content = data.get('content', '')
        
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        
        parent = None
        if parent_id:
            try:
                parent = VirtualFile.objects.get(id=parent_id, type=VirtualFile.FOLDER)
            except VirtualFile.DoesNotExist:
                return JsonResponse({'error': 'Parent folder not found'}, status=404)
        
        file = VirtualFile.objects.create(
            room_id=room_id,
            name=name,
            type=file_type,
            parent=parent,
            content=content if file_type == VirtualFile.FILE else '',
        )
        
        return JsonResponse(file.to_dict(), status=201)
    except IntegrityError:
        return JsonResponse({'error': 'A file with this name already exists in this location'}, status=409)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["PUT"])
def file_update_view(request, file_id):
    """
    Update a file's content.
    PUT body: { "content": "new content" }
    """
    try:
        file = VirtualFile.objects.get(id=file_id, type=VirtualFile.FILE)
        data = json.loads(request.body)
        
        if 'content' in data:
            file.content = data['content']
            file.save(update_fields=['content', 'updated_at'])
        
        return JsonResponse(file.to_dict())
    except VirtualFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["PUT"])
def file_rename_view(request, file_id):
    """
    Rename a file or folder.
    PUT body: { "name": "newname.js" }
    """
    try:
        file = VirtualFile.objects.get(id=file_id)
        data = json.loads(request.body)
        
        new_name = data.get('name')
        if not new_name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        
        file.name = new_name
        file.save(update_fields=['name', 'updated_at'])
        
        return JsonResponse(file.to_dict())
    except VirtualFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
    except IntegrityError:
        return JsonResponse({'error': 'A file with this name already exists in this location'}, status=409)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def file_delete_view(request, file_id):
    """
    Delete a file or folder (and all children if folder).
    """
    try:
        file = VirtualFile.objects.get(id=file_id)
        file.delete()  # CASCADE will delete children
        return JsonResponse({'success': True})
    except VirtualFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


@csrf_exempt
@require_http_methods(["PUT"])
def file_move_view(request, file_id):
    """
    Move a file or folder to a new parent.
    PUT body: { "parentId": "uuid" or null for root }
    """
    try:
        file = VirtualFile.objects.get(id=file_id)
        data = json.loads(request.body)
        
        parent_id = data.get('parentId')
        
        if parent_id:
            try:
                new_parent = VirtualFile.objects.get(id=parent_id, type=VirtualFile.FOLDER)
                # Prevent moving a folder into itself or its descendants
                if file.type == VirtualFile.FOLDER:
                    current = new_parent
                    while current:
                        if current.id == file.id:
                            return JsonResponse({'error': 'Cannot move folder into itself'}, status=400)
                        current = current.parent
                file.parent = new_parent
            except VirtualFile.DoesNotExist:
                return JsonResponse({'error': 'Parent folder not found'}, status=404)
        else:
            file.parent = None
        
        file.save(update_fields=['parent', 'updated_at'])
        return JsonResponse(file.to_dict())
    except VirtualFile.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
    except IntegrityError:
        return JsonResponse({'error': 'A file with this name already exists in the destination'}, status=409)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
