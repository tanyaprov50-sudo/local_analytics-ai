#!/bin/bash

echo "🧹 Полная очистка Docker ресурсов..."
echo ""

echo "🛑 Остановка всех контейнеров проекта..."
docker-compose down -v

echo "🗑️ Удаление неиспользуемых контейнеров..."
docker container prune -f

echo "🗑️ Удаление неиспользуемых сетей..."
docker network prune -f

echo "🗑️ Удаление неиспользуемых образов..."
docker image prune -f

echo ""
echo "✅ Очистка завершена!"
echo ""
echo "Теперь можете запустить: ./start.sh"
