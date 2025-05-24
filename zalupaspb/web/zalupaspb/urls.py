from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse

# Простая функция для проверки работоспособности
def healthcheck(request):
    return HttpResponse("OK! Django работает.", content_type="text/plain")

# Простая функция для главной страницы
def home(request):
    return HttpResponse("""
    <html>
        <head><title>ZalupaSPB</title></head>
        <body>
            <h1>ZalupaSPB</h1>
            <p>Система управления доступом ZalupaSPB успешно запущена!</p>
            <p><a href="/api/docs/">API Документация</a></p>
            <p><a href="/admin/">Админ-панель</a></p>
        </body>
    </html>
    """)

# Настройка API документации
schema_view = get_schema_view(
    openapi.Info(
        title="ZalupaSPB API",
        default_version='v1',
        description="API для системы управления доступом ZalupaSPB",
        contact=openapi.Contact(email="admin@zalupaspb.ru"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    # Главная страница
    path('', home),
    
    # Проверка работоспособности
    path('healthcheck/', healthcheck),
    
    # Админ-панель
    path('admin/', admin.site.urls),
    
    # API документация
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
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