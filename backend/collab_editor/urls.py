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
]
