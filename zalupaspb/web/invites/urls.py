from django.urls import path
from .views import (
    InviteListView, InviteDetailView, InviteCreateView, 
    InviteRevokeView, InviteValidateView
)

urlpatterns = [
    path('', InviteListView.as_view(), name='invite_list'),
    path('<uuid:pk>/', InviteDetailView.as_view(), name='invite_detail'),
    path('create/', InviteCreateView.as_view(), name='invite_create'),
    path('<uuid:pk>/revoke/', InviteRevokeView.as_view(), name='invite_revoke'),
    path('validate/', InviteValidateView.as_view(), name='invite_validate'),
] 