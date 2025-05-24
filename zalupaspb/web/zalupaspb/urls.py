from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

# Простая функция для проверки работоспособности
def healthcheck(request):
    return HttpResponse("OK! Django работает.", content_type="text/plain")

# Функция для главной страницы с использованием шаблона
def home(request):
    # Если пользователь авторизован - показываем ему панель управления
    if request.user.is_authenticated:
        # Здесь можно было бы сделать редирект на панель пользователя,
        # но пока оставим общую главную страницу
        pass
    
    return render(request, 'home.html')

# Функция для страницы документации API (доступна только авторизованным пользователям)
@login_required
def api_docs_view(request):
    return redirect('schema-swagger-ui')

# Функция для скачивания лоадера (доступна только авторизованным пользователям)
@login_required
def download_loader(request):
    # Здесь будет логика для скачивания последней версии лоадера
    from keys.models import Loader
    try:
        latest_loader = Loader.objects.filter(is_active=True).latest('upload_date')
        return redirect(latest_loader.file.url)
    except:
        # Если лоадера нет, перенаправляем на главную с сообщением
        return redirect('/?error=Лоадер не найден или вы не имеете прав для скачивания')

# Настройка API документации
schema_view = get_schema_view(
    openapi.Info(
        title="ZalupaSPB API",
        default_version='v1',
        description="API для системы управления доступом ZalupaSPB",
        contact=openapi.Contact(email="admin@zalupaspb.ru"),
        license=openapi.License(name="Proprietary"),
    ),
    public=False,  # Документация не публичная
    permission_classes=(permissions.IsAuthenticated,),  # Требуется аутентификация
)

urlpatterns = [
    # Главная страница
    path('', home, name='home'),
    
    # Проверка работоспособности
    path('healthcheck/', healthcheck, name='healthcheck'),
    
    # Админ-панель
    path('admin/', admin.site.urls),
    
    # Авторизация и регистрация
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/register/', include('users.urls.register')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Скачивание лоадера
    path('download/loader/', download_loader, name='download_loader'),
    
    # Ссылка на API документацию (с проверкой авторизации)
    path('api/docs/', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='schema-swagger-ui'),
    path('api/docs/redoc/', login_required(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
    
    # API endpoints
    path('api/auth/', include('users.urls.auth')),
    path('api/users/', include('users.urls.users')),
    path('api/keys/', include('keys.urls')),
    path('api/invites/', include('invites.urls')),
    path('api/logs/', include('logs.urls')),
]

# Добавление обработки статических и медиа файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 