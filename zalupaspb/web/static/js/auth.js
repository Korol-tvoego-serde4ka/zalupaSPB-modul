document.addEventListener('DOMContentLoaded', function() {
    // Улучшаем поля ввода формы
    enhanceFormInputs();
    
    // Инициализируем валидацию формы
    initFormValidation();
    
    // Добавляем анимации для появления элементов
    animateAuthElements();
    
    // Обработка сообщений об ошибках и успехе
    const messages = document.querySelectorAll('.alert');
    if (messages.length > 0) {
        // Автоматически скрыть сообщения через 5 секунд
        messages.forEach(message => {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.style.display = 'none';
                }, 300);
            }, 5000);
        });
    }
    
    // Валидация формы регистрации
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password1 = document.getElementById('password1');
            const password2 = document.getElementById('password2');
            const inviteCode = document.getElementById('invite_code');
            
            // Проверка паролей
            if (password1 && password2 && password1.value !== password2.value) {
                e.preventDefault();
                const errorDiv = document.createElement('div');
                errorDiv.className = 'form-error';
                errorDiv.textContent = 'Пароли не совпадают';
                
                // Проверяем, нет ли уже ошибки
                const existingError = password2.parentNode.querySelector('.form-error');
                if (!existingError) {
                    password2.parentNode.appendChild(errorDiv);
                }
                
                password2.focus();
            }
            
            // Проверка инвайт-кода
            if (inviteCode && inviteCode.value.trim() === '') {
                e.preventDefault();
                const errorDiv = document.createElement('div');
                errorDiv.className = 'form-error';
                errorDiv.textContent = 'Код приглашения обязателен';
                
                // Проверяем, нет ли уже ошибки
                const existingError = inviteCode.parentNode.querySelector('.form-error');
                if (!existingError) {
                    inviteCode.parentNode.appendChild(errorDiv);
                }
                
                inviteCode.focus();
            }
        });
    }
    
    // Анимация появления формы
    const authCard = document.querySelector('.auth-card');
    if (authCard) {
        authCard.style.opacity = '0';
        authCard.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            authCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            authCard.style.opacity = '1';
            authCard.style.transform = 'translateY(0)';
        }, 100);
    }
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