@echo off
echo 🚀 Запуск локального аналитика...
echo.

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose не установлен. Установите Docker Compose: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo ✅ Docker найден
echo.

REM Остановка старых контейнеров
echo 🛑 Остановка старых контейнеров...
docker-compose down

REM Очистка старых контейнеров и сетей
echo 🧹 Очистка старых ресурсов...
docker container prune -f
docker network prune -f

REM Сборка и запуск
echo 🔨 Сборка и запуск контейнеров...
docker-compose up --build -d

echo.
echo ⏳ Ожидание запуска сервисов...
timeout /t 5 /nobreak >nul

REM Проверка статуса
echo.
echo 📊 Статус сервисов:
docker-compose ps

echo.
echo ✅ Система запущена!
echo.
echo 🌐 Откройте в браузере: http://localhost:3000
echo.
echo 📝 Полезные команды:
echo   - Просмотр логов:     docker-compose logs -f
echo   - Остановка:          docker-compose down
echo   - Перезапуск:         docker-compose restart
echo.
pause
