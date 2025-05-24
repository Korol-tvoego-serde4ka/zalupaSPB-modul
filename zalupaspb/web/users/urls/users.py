from django.urls import path
from ..views.users import (
    UserListView, UserDetailView, UserUpdateView, UserDeleteView, 
    UserBanView, UserUnbanView, UserRoleUpdateView,
    DiscordBindingCodeView, DiscordBindView
)

urlpatterns = [
    # Управление пользователями
    path('', UserListView.as_view(), name='user_list'),
    path('<uuid:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('<uuid:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('<uuid:pk>/ban/', UserBanView.as_view(), name='user_ban'),
    path('<uuid:pk>/unban/', UserUnbanView.as_view(), name='user_unban'),
    path('<uuid:pk>/role/', UserRoleUpdateView.as_view(), name='user_role_update'),
    
    # Привязка Discord
    path('binding/code/', DiscordBindingCodeView.as_view(), name='discord_binding_code'),
    path('binding/discord/', DiscordBindView.as_view(), name='discord_bind'),
] 