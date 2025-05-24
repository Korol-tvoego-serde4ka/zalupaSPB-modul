from django.urls import path
from .views import (
    KeyListView, KeyDetailView, KeyCreateView, KeyActivateView, KeyRevokeView
)

urlpatterns = [
    path('', KeyListView.as_view(), name='key_list'),
    path('<uuid:pk>/', KeyDetailView.as_view(), name='key_detail'),
    path('create/', KeyCreateView.as_view(), name='key_create'),
    path('<uuid:pk>/activate/', KeyActivateView.as_view(), name='key_activate'),
    path('<uuid:pk>/revoke/', KeyRevokeView.as_view(), name='key_revoke'),
] 