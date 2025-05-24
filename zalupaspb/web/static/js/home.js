document.addEventListener('DOMContentLoaded', function() {
    // Анимация для карточек с возможностями системы
    const featureCards = document.querySelectorAll('.feature-card');
    animateOnScroll(featureCards);
    
    // Анимация для карточек с ролями
    const roleCards = document.querySelectorAll('.role-card');
    animateOnScroll(roleCards, 150);
    
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