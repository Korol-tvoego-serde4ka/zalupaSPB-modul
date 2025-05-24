from django.urls import path
from users.views.auth import RegisterView

app_name = 'accounts'

urlpatterns = [
    path('', RegisterView.as_view(), name='register'),
] 