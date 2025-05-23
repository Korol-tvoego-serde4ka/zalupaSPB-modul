# Руководство администратора ZalupaSPB

Данное руководство предназначено для администраторов и модераторов системы ZalupaSPB и описывает расширенные функции управления.

## Роли пользователей

В системе ZalupaSPB существуют следующие роли пользователей:

| Роль | Описание | Возможности |
|------|----------|-------------|
| Admin | Администратор системы | Полный доступ ко всем функциям |
| Moderator | Модератор | Управление пользователями, ключами и инвайтами |
| Support | Поддержка | Просмотр информации, блокировка пользователей |
| User | Обычный пользователь | Базовые функции использования системы |

## Панель администратора

### Доступ к панели администратора

Для доступа к панели администратора:

1. Войдите в систему с учетной записью администратора или модератора
2. Нажмите на значок шестеренки ⚙️ в верхнем правом углу
3. Выберите "Панель администратора"

### Обзор функций панели администратора

Панель администратора предоставляет доступ к следующим разделам:

- **Пользователи**: Управление пользователями системы
- **Ключи**: Управление ключами доступа
- **Инвайты**: Управление инвайт-кодами
- **Логи**: Просмотр системных логов
- **Настройки**: Глобальные настройки системы

## Управление пользователями

### Просмотр списка пользователей

Для просмотра списка пользователей:

1. В панели администратора перейдите в раздел "Пользователи"
2. Используйте фильтры для поиска конкретных пользователей:
   - По имени пользователя
   - По роли
   - По статусу (заблокирован/активен)
   - По Discord ID
   - По пригласившему пользователю

### Создание пользователя

Администраторы могут создавать пользователей напрямую:

1. В разделе "Пользователи" нажмите кнопку "Создать пользователя"
2. Заполните необходимые поля:
   - Имя пользователя
   - Email
   - Пароль
   - Роль
   - Лимит инвайтов
3. Нажмите кнопку "Создать"

### Редактирование пользователя

Для изменения данных пользователя:

1. Найдите пользователя в списке
2. Нажмите на кнопку "Редактировать"
3. Внесите необходимые изменения
4. Нажмите кнопку "Сохранить"

Администраторы могут изменять все данные пользователя, включая роль. Модераторы не могут изменять роли или лимиты инвайтов.

### Блокировка пользователя

Для блокировки пользователя:

1. Найдите пользователя в списке
2. Нажмите на кнопку "Заблокировать"
3. Укажите причину блокировки
4. Нажмите кнопку "Подтвердить"

Заблокированные пользователи не могут входить в систему или использовать API.

### Разблокировка пользователя

Для разблокировки пользователя:

1. Найдите пользователя в списке (используйте фильтр "Заблокированные")
2. Нажмите на кнопку "Разблокировать"
3. Подтвердите действие

### Удаление пользователя

Для удаления пользователя (только администраторы):

1. Найдите пользователя в списке
2. Нажмите на кнопку "Удалить"
3. Подтвердите действие

**Внимание**: Удаление пользователя - необратимая операция. Все данные пользователя, включая созданные им инвайты и ключи, будут удалены.

## Управление ключами

### Просмотр списка ключей

Для просмотра списка ключей:

1. В панели администратора перейдите в раздел "Ключи"
2. Используйте фильтры для поиска конкретных ключей:
   - По типу ключа (стандартный, премиум, пожизненный)
   - По статусу (активный, использованный, истекший, отозванный)
   - По создателю
   - По активировавшему пользователю

### Создание ключа

Администраторы и модераторы могут создавать ключи:

1. В разделе "Ключи" нажмите кнопку "Создать ключ"
2. Выберите тип ключа:
   - Стандартный (30 дней)
   - Премиум (90 дней)
   - Пожизненный
3. Укажите срок действия (для стандартных и премиум ключей)
4. При необходимости добавьте примечание
5. Нажмите кнопку "Создать"

### Отзыв ключа

Для отзыва активного ключа:

1. Найдите ключ в списке
2. Нажмите на кнопку "Отозвать"
3. Подтвердите действие

Отозванные ключи не могут быть использованы для активации.

### Генерация нескольких ключей

Для создания нескольких ключей одновременно (массовая генерация):

1. В разделе "Ключи" нажмите кнопку "Массовая генерация"
2. Выберите тип ключа
3. Укажите количество ключей для генерации
4. Укажите срок действия
5. При необходимости добавьте примечание
6. Нажмите кнопку "Сгенерировать"

### Экспорт ключей

Для экспорта списка ключей:

1. Примените необходимые фильтры для выбора ключей
2. Нажмите кнопку "Экспорт"
3. Выберите формат экспорта (CSV, JSON, TXT)
4. Загрузите файл с ключами

## Управление инвайтами

### Просмотр списка инвайтов

Для просмотра списка инвайтов:

1. В панели администратора перейдите в раздел "Инвайты"
2. Используйте фильтры для поиска конкретных инвайтов:
   - По статусу (активный, использованный, истекший, отозванный)
   - По создателю
   - По использовавшему пользователю

### Создание инвайта

Администраторы и модераторы могут создавать инвайты без ограничений:

1. В разделе "Инвайты" нажмите кнопку "Создать инвайт"
2. Укажите срок действия инвайта (по умолчанию 7 дней)
3. Нажмите кнопку "Создать"

### Отзыв инвайта

Для отзыва активного инвайта:

1. Найдите инвайт в списке
2. Нажмите на кнопку "Отозвать"
3. Подтвердите действие

Отозванные инвайты не могут быть использованы для регистрации.

### Управление лимитами инвайтов

Администраторы могут управлять лимитами инвайтов для пользователей:

1. В разделе "Настройки" выберите вкладку "Инвайты"
2. Настройте лимиты инвайтов для каждой роли:
   - Администраторы (по умолчанию: неограниченно)
   - Модераторы (по умолчанию: 10 в месяц)
   - Поддержка (по умолчанию: 0)
   - Пользователи (по умолчанию: 2 в месяц)
3. Нажмите кнопку "Сохранить"

Для изменения лимита конкретного пользователя:

1. Перейдите в раздел "Пользователи"
2. Найдите пользователя и нажмите "Редактировать"
3. Измените значение "Лимит инвайтов в месяц"
4. Нажмите кнопку "Сохранить"

## Система логирования

### Просмотр логов

Для просмотра системных логов:

1. В панели администратора перейдите в раздел "Логи"
2. Используйте фильтры для поиска конкретных записей:
   - По уровню (отладка, информация, предупреждение, ошибка, критическая ошибка)
   - По категории (пользователи, ключи, инвайты, Discord, система, безопасность)
   - По пользователю
   - По IP-адресу
   - По временному диапазону
   - По тексту сообщения

### Экспорт логов

Для экспорта логов:

1. Примените необходимые фильтры
2. Нажмите кнопку "Экспорт"
3. Выберите формат экспорта (CSV, JSON)
4. Загрузите файл с логами

### Настройка логирования

Администраторы могут настроить параметры логирования:

1. В разделе "Настройки" выберите вкладку "Логирование"
2. Настройте параметры:
   - Уровень логирования
   - Хранение логов (количество дней)
   - Отправка критических ошибок на email
   - Настройка webhook Discord для логов
3. Нажмите кнопку "Сохранить"

## Интеграция с Discord

### Настройка Discord-бота

Для настройки интеграции с Discord:

1. В разделе "Настройки" выберите вкладку "Discord"
2. Настройте параметры:
   - Токен бота
   - ID сервера
   - ID каналов (логи, ошибки, модерация)
   - ID ролей (администратор, модератор, поддержка, пользователь)
3. Нажмите кнопку "Сохранить"
4. Нажмите кнопку "Проверить подключение" для проверки настроек

### Управление ролями Discord

Система автоматически синхронизирует роли пользователей с ролями в Discord. Для настройки соответствия ролей:

1. В разделе "Настройки" выберите вкладку "Discord"
2. В блоке "Соответствие ролей" настройте соответствие между ролями в системе и ролями в Discord
3. Нажмите кнопку "Сохранить"

### Команды модерации через Discord

Администраторы и модераторы могут использовать Discord-бота для управления системой:

- `/generate_key [type] [duration]` - Генерация ключа
- `/ban @user [reason]` - Блокировка пользователя
- `/unban @user` - Разблокировка пользователя
- `/stats @user` - Просмотр статистики пользователя

## Настройки системы

### Общие настройки

В разделе "Настройки" > "Общие" администраторы могут настроить:

- Название системы
- Контактный email
- Регистрация новых пользователей (включено/выключено)
- Режим обслуживания (включено/выключено)
- Сообщение при режиме обслуживания

### Настройки безопасности

В разделе "Настройки" > "Безопасность" администраторы могут настроить:

- Минимальная длина пароля
- Сложность пароля (требования к паролям)
- Время жизни сессии
- Максимальное количество неудачных попыток входа
- Время блокировки после неудачных попыток
- Двухфакторная аутентификация (включено/выключено)

### Настройки ключей

В разделе "Настройки" > "Ключи" администраторы могут настроить:

- Типы ключей и их параметры
- Срок действия по умолчанию для каждого типа
- Формат генерируемых ключей

### Резервное копирование

Для создания резервной копии базы данных:

1. В разделе "Настройки" выберите вкладку "Резервное копирование"
2. Нажмите кнопку "Создать резервную копию"
3. После завершения процесса нажмите кнопку "Скачать"

Для восстановления из резервной копии:

1. В разделе "Настройки" выберите вкладку "Резервное копирование"
2. Нажмите кнопку "Загрузить резервную копию"
3. Выберите файл резервной копии
4. Нажмите кнопку "Восстановить"
5. Подтвердите действие

**Внимание**: Восстановление из резервной копии перезапишет все текущие данные в системе.

## Рекомендации по безопасности

1. **Регулярно меняйте пароли** администраторских учетных записей
2. **Используйте двухфакторную аутентификацию** для всех административных аккаунтов
3. **Регулярно проверяйте журналы** на наличие подозрительной активности
4. **Ограничьте доступ к панели администратора** по IP-адресам
5. **Создавайте резервные копии** базы данных регулярно
6. **Следите за обновлениями** системы и устанавливайте их своевременно
7. **Не выдавайте права администратора** без крайней необходимости

## Устранение неполадок

### Проблемы с Discord-ботом

Если Discord-бот не работает:

1. Проверьте статус бота в разделе "Настройки" > "Discord"
2. Убедитесь, что токен бота указан правильно
3. Проверьте журнал ошибок бота в файле `zalupaspb/bot/bot.log`
4. Перезапустите бота кнопкой "Перезапустить бота" в настройках

### Проблемы с доступом к панели администратора

Если у вас возникли проблемы с доступом к панели администратора:

1. Убедитесь, что ваш аккаунт имеет роль администратора или модератора
2. Проверьте, не включен ли режим обслуживания
3. Очистите кеш браузера и cookies
4. Если проблема не решена, восстановите пароль через функцию восстановления

### Критические ошибки

В случае критических ошибок:

1. Проверьте журнал ошибок в разделе "Логи"
2. Проверьте файлы логов на сервере:
   - Логи Django: `zalupaspb/web/logs/django.log`
   - Логи приложения: `zalupaspb/web/logs/app.log`
   - Логи бота: `zalupaspb/bot/bot.log`
3. При необходимости восстановите систему из резервной копии 