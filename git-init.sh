#!/bin/bash

echo "Инициализация Git репозитория..."

git init
git add .
git commit -m "Initial commit: Локальный аналитик с AI"

echo ""
echo "Готово! Теперь создайте репозиторий на GitHub и выполните:"
echo ""
echo "git remote add origin https://github.com/YOUR_USERNAME/local-analytics-ai.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
