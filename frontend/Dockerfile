FROM node:18-alpine as build

WORKDIR /app

# Копируем package.json (если есть) или создаём минимальный
COPY package*.json ./

# Устанавливаем зависимости (если нужны)
RUN npm install --production || true

# Копируем статические файлы
COPY static ./static
COPY templates ./templates

# Production stage - используем nginx для раздачи статики
FROM nginx:alpine

# Копируем статические файлы
COPY --from=build /app/static /usr/share/nginx/html/static
COPY --from=build /app/templates /usr/share/nginx/html/templates

# Копируем конфигурацию nginx из папки frontend
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
