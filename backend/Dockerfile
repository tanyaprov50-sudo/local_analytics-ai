FROM python:3.11-slim

WORKDIR /app

# Копируем requirements из корня проекта
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения из корня
COPY app.py .
COPY backend/ ./backend/
COPY templates/ ./templates/
COPY static/ ./static/

# Создаём папку для загрузок
RUN mkdir -p uploads

# Открываем порт
EXPOSE 5000

# Запускаем Flask
CMD ["python", "app.py"]
