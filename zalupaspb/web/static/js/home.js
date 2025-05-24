document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления карточек с возможностями
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards.length > 0) {
        // Применяем задержку для каждой карточки, чтобы они появлялись по очереди
        featureCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 * (index + 1));
        });
    }

    // Анимация для кнопок
    const buttons = document.querySelectorAll('.btn');
    if (buttons.length > 0) {
        buttons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-3px)';
                this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.15)';
            });

            button.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
            });
        });
    }

    // Проверка наличия сообщений об ошибках или успехе в URL
    const urlParams = new URLSearchParams(window.location.search);
    const errorMsg = urlParams.get('error');
    const successMsg = urlParams.get('success');
    
    // Показать сообщение, если оно есть
    if (errorMsg) {
        showMessage(errorMsg, 'error');
    } else if (successMsg) {
        showMessage(successMsg, 'success');
    }

    // Инициализация мобильного меню
    initMobileMenu();
    
    // Плавная прокрутка для якорных ссылок
    initSmoothScroll();
});

/**
 * Инициализирует мобильное меню
 */
function initMobileMenu() {
    const menuButton = document.querySelector('.mobile-menu-button');
    const nav = document.querySelector('nav ul');
    
    if (!menuButton || !nav) return;
    
    menuButton.addEventListener('click', function() {
        this.classList.toggle('active');
        nav.classList.toggle('active');
    });
    
    // Закрывать меню при клике на пункт меню
    const menuItems = nav.querySelectorAll('a');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            menuButton.classList.remove('active');
            nav.classList.remove('active');
        });
    });
}

/**
 * Анимирует элементы при прокрутке страницы
 * @param {NodeList} elements - Элементы для анимации
 * @param {number} delay - Задержка между анимациями (мс)
 */
function animateOnScroll(elements, delay = 100) {
    if (!elements.length) return;
    
    const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animated');
                }, index * delay);
                observer.unobserve(entry.target);
            }
        });
    }, options);
    
    elements.forEach(element => {
        observer.observe(element);
    });
}

/**
 * Инициализирует плавную прокрутку для якорных ссылок
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (!targetElement) return;
            
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        });
    });
}

// Функция для отображения всплывающего сообщения
function showMessage(message, type = 'info') {
    // Создаем элемент для сообщения
    const messageEl = document.createElement('div');
    messageEl.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'}`;
    messageEl.textContent = message;
    
    // Добавляем стили для анимации
    messageEl.style.position = 'fixed';
    messageEl.style.top = '20px';
    messageEl.style.left = '50%';
    messageEl.style.transform = 'translateX(-50%)';
    messageEl.style.zIndex = '1000';
    messageEl.style.opacity = '0';
    messageEl.style.transition = 'opacity 0.3s ease';
    
    // Добавляем в DOM
    document.body.appendChild(messageEl);
    
    // Запускаем анимацию появления
    setTimeout(() => {
        messageEl.style.opacity = '1';
    }, 10);
    
    // Автоматически скрываем через 5 секунд
    setTimeout(() => {
        messageEl.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(messageEl);
        }, 300);
    }, 5000);
} 