from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib import messages

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
        keys = request.user.keys.all().order_by('-activated_at')
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
    
    context = {}
    
    if request.method == 'POST':
        key_code = request.POST.get('key_code')
        
        # Проверка существования и валидности ключа по key_code вместо key
        try:
            key = Key.objects.get(key_code=key_code)
            
            if key.is_used:
                messages.error(request, 'Этот ключ уже был использован')
            elif key.is_expired:
                messages.error(request, 'Срок действия ключа истек')
            else:
                # Активируем ключ для текущего пользователя
                key.activate(request.user)
                messages.success(request, 'Ключ успешно активирован')
                context['activated_key'] = key
        except Key.DoesNotExist:
            messages.error(request, 'Ключ не найден')
    
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