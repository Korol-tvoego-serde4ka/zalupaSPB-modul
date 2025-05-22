FROM node:16-alpine

WORKDIR /app

# Копирование файлов package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production

# Копирование исходного кода
COPY . .

# Создание директории для логов
RUN mkdir -p logs

# Установка рабочего каталога
ENV NODE_ENV=production

# Открываем порт
EXPOSE 3000

# Запуск приложения
CMD ["node", "src/app.js"] 