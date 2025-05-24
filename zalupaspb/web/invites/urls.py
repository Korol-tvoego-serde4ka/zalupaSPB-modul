from django.urls import path
from .views import (
    InviteDetailView, InviteCreateView, 
    InviteRevokeView, InviteValidateView
)

urlpatterns = [
    # Корневой URL для получения списка (GET) или создания (POST) инвайтов
    path('', InviteCreateView.as_view(), name='invite_create_or_list'),
    path('<uuid:pk>/', InviteDetailView.as_view(), name='invite_detail'),
    path('<uuid:pk>/revoke/', InviteRevokeView.as_view(), name='invite_revoke'),
    path('validate/', InviteValidateView.as_view(), name='invite_validate'),
] 