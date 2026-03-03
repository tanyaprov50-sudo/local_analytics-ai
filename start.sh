#!/bin/bash

echo "🚀 Запуск локального аналитика..."
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker найден"
echo ""

# Остановка старых контейнеров
echo "🛑 Остановка старых контейнеров..."
docker-compose down

# Очистка старых контейнеров и сетей
echo "🧹 Очистка старых ресурсов..."
docker container prune -f
docker network prune -f

# Сборка и запуск
echo "🔨 Сборка и запуск контейнеров..."
docker-compose up --build -d

echo ""
echo "⏳ Ожидание запуска сервисов..."
sleep 5

# Проверка статуса
echo ""
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "✅ Система запущена!"
echo ""
echo "🌐 Откройте в браузере: http://localhost:3000"
echo ""
echo "📝 Полезные команды:"
echo "  - Просмотр логов:     docker-compose logs -f"
echo "  - Остановка:          docker-compose down"
echo "  - Перезапуск:         docker-compose restart"
echo ""
