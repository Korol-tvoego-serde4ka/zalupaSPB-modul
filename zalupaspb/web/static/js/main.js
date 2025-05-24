document.addEventListener('DOMContentLoaded', function() {
    // Инициализация мобильного меню
    initMobileMenu();
    
    // Обработка нажатий на ссылки
    handleLinks();
    
    // Добавление класса "loaded" к body для анимаций при загрузке
    document.body.classList.add('loaded');

    // Анимация для элементов при прокрутке
    function checkVisibility() {
        const elements = document.querySelectorAll('.feature-card');
        const windowHeight = window.innerHeight;
        
        elements.forEach(element => {
            const position = element.getBoundingClientRect();
            
            // Проверяем, виден ли элемент в окне просмотра
            if(position.top < windowHeight * 0.9) {
                element.classList.add('visible');
            }
        });
    }

    // Инициализация при загрузке страницы
    checkVisibility();
    
    // Проверка при прокрутке
    window.addEventListener('scroll', checkVisibility);
});

/**
 * Инициализирует мобильное меню
 */
function initMobileMenu() {
    const menuButton = document.querySelector('.mobile-menu-button');
    const nav = document.querySelector('header nav ul');
    
    if (!menuButton || !nav) return;
    
    menuButton.addEventListener('click', function() {
        this.classList.toggle('active');
        nav.classList.toggle('active');
        document.body.classList.toggle('menu-open');
    });
    
    // Закрываем меню при клике на ссылку
    const menuLinks = nav.querySelectorAll('a');
    menuLinks.forEach(link => {
        link.addEventListener('click', function() {
            menuButton.classList.remove('active');
            nav.classList.remove('active');
            document.body.classList.remove('menu-open');
        });
    });
    
    // Закрываем меню при клике вне его
    document.addEventListener('click', function(event) {
        if (!nav.contains(event.target) && !menuButton.contains(event.target) && nav.classList.contains('active')) {
            menuButton.classList.remove('active');
            nav.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    });
}

/**
 * Обрабатывает нажатия на ссылки
 */
function handleLinks() {
    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Пропускаем, если это не якорная ссылка или она ведет на # (наверх страницы)
            if (href === '#' || href.indexOf('#') !== 0) return;
            
            e.preventDefault();
            
            const targetId = href;
            const targetElement = document.querySelector(targetId);
            
            if (!targetElement) return;
            
            const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset;
            
            window.scrollTo({
                top: offsetTop - 80, // Учитываем высоту шапки
                behavior: 'smooth'
            });
        });
    });
    
    // Добавляем класс active к текущей странице в меню
    const currentUrl = window.location.pathname;
    document.querySelectorAll('nav a').forEach(link => {
        const linkUrl = link.getAttribute('href');
        if (linkUrl === currentUrl || (currentUrl === '/' && linkUrl === '/')) {
            link.classList.add('active');
        }
    });
} 