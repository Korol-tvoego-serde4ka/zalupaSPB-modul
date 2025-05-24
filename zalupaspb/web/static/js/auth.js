document.addEventListener('DOMContentLoaded', function() {
    // Улучшаем поля ввода формы
    enhanceFormInputs();
    
    // Инициализируем валидацию формы
    initFormValidation();
    
    // Добавляем анимации для появления элементов
    animateAuthElements();
});

/**
 * Улучшает поля ввода формы, добавляя классы активности и фокуса
 */
function enhanceFormInputs() {
    const formInputs = document.querySelectorAll('.form-group input');
    
    formInputs.forEach(input => {
        // Добавляем класс active, если поле уже содержит текст
        if (input.value !== '') {
            input.classList.add('active');
        }
        
        // Обработчики событий для добавления/удаления классов
        input.addEventListener('focus', function() {
            this.classList.add('focus');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('focus');
            if (this.value !== '') {
                this.classList.add('active');
            } else {
                this.classList.remove('active');
            }
        });
    });
}

/**
 * Инициализирует простую валидацию формы
 */
function initFormValidation() {
    const loginForm = document.querySelector('form');
    
    if (!loginForm) return;
    
    loginForm.addEventListener('submit', function(e) {
        let isValid = true;
        const username = this.querySelector('input[name="username"]');
        const password = this.querySelector('input[name="password"]');
        
        // Очищаем предыдущие ошибки
        clearValidationErrors();
        
        // Проверяем, что поля не пустые
        if (!username.value.trim()) {
            showValidationError(username, 'Имя пользователя не может быть пустым');
            isValid = false;
        }
        
        if (!password.value.trim()) {
            showValidationError(password, 'Пароль не может быть пустым');
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
}

/**
 * Отображает ошибку валидации для указанного поля
 * @param {HTMLElement} input - Поле ввода
 * @param {string} message - Сообщение об ошибке
 */
function showValidationError(input, message) {
    const formGroup = input.closest('.form-group');
    const errorElement = document.createElement('div');
    
    errorElement.className = 'input-error';
    errorElement.textContent = message;
    
    formGroup.classList.add('has-error');
    formGroup.appendChild(errorElement);
}

/**
 * Очищает все ошибки валидации
 */
function clearValidationErrors() {
    document.querySelectorAll('.input-error').forEach(error => error.remove());
    document.querySelectorAll('.form-group.has-error').forEach(group => {
        group.classList.remove('has-error');
    });
}

/**
 * Добавляет анимации для элементов формы авторизации
 */
function animateAuthElements() {
    const authCard = document.querySelector('.auth-card');
    
    if (!authCard) return;
    
    // Добавляем класс для анимации появления
    setTimeout(() => {
        authCard.classList.add('animated');
    }, 100);
    
    // Анимируем дочерние элементы последовательно
    const childElements = authCard.children;
    let delay = 200;
    
    for (let i = 0; i < childElements.length; i++) {
        const element = childElements[i];
        setTimeout(() => {
            element.classList.add('animated');
        }, delay);
        delay += 100;
    }
} 