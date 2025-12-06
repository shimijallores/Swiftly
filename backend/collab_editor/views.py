from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json

from .models import CollabUser


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
