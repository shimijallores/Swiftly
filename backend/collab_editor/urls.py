from django.urls import path
from . import views

urlpatterns = [
    path('api/user/', views.get_or_create_user, name='get_or_create_user'),
    path('api/user/<str:client_id>/', views.update_user, name='update_user'),
]
