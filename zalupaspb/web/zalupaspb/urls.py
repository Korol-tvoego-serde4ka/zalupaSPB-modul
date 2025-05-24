from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib import messages
import logging

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

# Функция для страницы профиля пользователя
@login_required
def profile_view(request):
    # Получаем инвайты, созданные пользователем
    try:
        invites = request.user.created_invites.all().order_by('-created_at')
    except:
        invites = []
    
    # Получаем ключи, привязанные к пользователю
    try:
        keys = request.user.activated_keys.all().order_by('-activated_at')
    except:
        keys = []
    
    context = {
        'user': request.user,
        'invites': invites,
        'keys': keys
    }
    
    return render(request, 'profile.html', context)

# Функция для активации ключа
@login_required
def activate_key_view(request):
    from keys.models import Key
    
    logger = logging.getLogger('keys')
    context = {}
    
    if request.method == 'POST':
        key_code = request.POST.get('key_code')
        # Получаем IP пользователя
        ip_address = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR', ''))
        
        # Добавляем информацию о пользователе и IP в лог
        extra = {
            'user_id': request.user.id,
            'ip_address': ip_address
        }
        logger.info(f"Попытка активации ключа: {key_code} пользователем {request.user.username}", extra=extra)
        
        if not key_code:
            messages.error(request, 'Пожалуйста, введите код ключа')
            logger.warning(f"Пользователь {request.user.username} не ввел код ключа", extra=extra)
            return render(request, 'activate_key.html', context)
        
        # Проверка существования и валидности ключа по key_code
        try:
            key = Key.objects.get(key_code=key_code)
            
            if key.status == Key.KeyStatus.USED:
                messages.error(request, 'Этот ключ уже был использован')
                logger.warning(f"Ключ {key_code} уже был использован", extra=extra)
            elif key.status == Key.KeyStatus.EXPIRED:
                messages.error(request, 'Срок действия ключа истек')
                logger.warning(f"Ключ {key_code} истек", extra=extra)
            elif key.status == Key.KeyStatus.REVOKED:
                messages.error(request, 'Этот ключ был отозван')
                logger.warning(f"Ключ {key_code} отозван", extra=extra)
            elif key.status == Key.KeyStatus.ACTIVE:
                # Активируем ключ для текущего пользователя
                if key.activate(request.user):
                    messages.success(request, 'Ключ успешно активирован')
                    logger.info(f"Ключ {key_code} успешно активирован пользователем {request.user.username}", extra=extra)
                    context['activated_key'] = key
                else:
                    messages.error(request, 'Не удалось активировать ключ')
                    logger.error(f"Ошибка активации ключа {key_code} пользователем {request.user.username}", extra=extra)
            else:
                messages.error(request, 'Ключ не может быть активирован')
                logger.warning(f"Ключ {key_code} имеет некорректный статус: {key.status}", extra=extra)
        except Key.DoesNotExist:
            messages.error(request, 'Ключ не найден')
            logger.warning(f"Ключ не найден: {key_code}", extra=extra)
    
    return render(request, 'activate_key.html', context)

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

urlpatterns = [
    # Главная страница
    path('', home, name='home'),
    
    # Профиль пользователя
    path('profile/', profile_view, name='profile'),
    
    # Важно: дополнительный маршрут для обработки стандартного URL профиля Django
    path('accounts/profile/', profile_view, name='accounts_profile'),
    
    # Активация ключа
    path('key/activate/', activate_key_view, name='activate_key'),
    
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