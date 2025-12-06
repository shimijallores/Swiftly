from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import CollabUser


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
