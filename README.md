# 📊 Локальный Аналитик

Полностью локальная аналитическая система с AI. Без облака, без ключей, без интернета.

![Status](https://img.shields.io/badge/status-ready-brightgreen)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Возможности

- ✅ Анализ Excel (XLSX, XLS), CSV и PDF файлов
- ✅ Базовая статистика и визуализация данных (графики)
- ✅ AI-анализ через локальную LLM (Ollama + gemma3:1b)
- ✅ Генерация PDF-отчётов
- ✅ Современный минималистичный интерфейс
- ✅ Анимация котика-аналитика при обработке 🐱
- ✅ Полностью локально (без облачных сервисов)

## 🏗️ Архитектура

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend   │─────▶│   Ollama    │
│  (Docker)   │      │  (Docker)   │      │  (Локально) │
│  Port 3000  │      │  Port 5000  │      │  Port 11434 │
└─────────────┘      └─────────────┘      └─────────────┘
```

**Компоненты:**
- **Frontend**: Nginx + Vanilla JS + Chart.js
- **Backend**: Flask + Pandas + pdfplumber
- **AI**: Ollama (gemma3:1b, 815MB)

## 🚀 Быстрый старт

### Требования

- Docker + Docker Compose
- Ollama (установлена локально)
- 2GB+ RAM

### 1. Установка Ollama

**Windows:**
```powershell
winget install Ollama.Ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

### 2. Запуск Ollama

В отдельном терминале:
```bash
ollama serve
```

### 3. Загрузка модели

```bash
ollama pull gemma3:1b
```

### 4. Запуск проекта

**Скопируйте .env.example (опционально):**
```bash
cp .env.example .env
```

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Или вручную:**
```bash
docker-compose up --build
```

### 5. Открыть в браузере

```
http://localhost:3000
```

## 📖 Использование

1. Откройте http://localhost:3000
2. Загрузите файл (Excel, CSV или PDF)
3. Просмотрите базовую аналитику и графики
4. Нажмите "🤖 Проанализировать с AI" для AI-анализа
5. Скачайте PDF-отчёт

## 🔧 Настройка

### Смена модели

Отредактируйте `docker-compose.yml`:

```yaml
backend:
  environment:
    - OLLAMA_MODEL=phi3:mini  # Или другая модель
```

Затем:
```bash
ollama pull phi3:mini
docker-compose restart backend
```

### Доступные модели

| Модель | Размер | RAM | Скорость | Качество |
|--------|--------|-----|----------|----------|
| gemma3:1b | 815MB | 2GB | ⚡⚡⚡ | ⭐⭐ |
| phi3:mini | 2.3GB | 4GB | ⚡⚡ | ⭐⭐⭐ |
| mistral:7b | 4.1GB | 8GB | ⚡ | ⭐⭐⭐⭐ |
| llama3:8b | 4.7GB | 8GB | ⚡ | ⭐⭐⭐⭐⭐ |

Полный список: https://ollama.com/library

## 🛠️ Troubleshooting

### Ollama не отвечает

```bash
# Проверьте, запущена ли Ollama
curl http://localhost:11434/api/tags

# Если нет, запустите
ollama serve
```

### Модель не загружена

```bash
# Проверьте модели
ollama list

# Загрузите gemma3:1b
ollama pull gemma3:1b
```

### Backend не подключается к Ollama

Убедитесь:
1. Ollama запущена: `ollama serve`
2. Модель загружена: `ollama list`
3. Backend видит Ollama: `docker-compose logs backend`

### Порты заняты

Измените в `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "8080:3000"  # Вместо 3000

backend:
  ports:
    - "8000:5000"  # Вместо 5000
```

## 📁 Структура проекта

```
.
├── backend/
│   ├── services/
│   │   ├── __init__.py
│   │   └── llm_service.py      # Интеграция с Ollama
│   └── Dockerfile
├── frontend/
│   ├── static/                 # CSS, JS
│   ├── templates/              # HTML
│   ├── Dockerfile
│   └── nginx.conf
├── static/
│   ├── script.js               # Frontend логика
│   └── style.css               # Дизайн + анимация котика
├── templates/
│   └── index.html
├── uploads/                    # Загруженные файлы
├── app.py                      # Flask приложение
├── requirements.txt
├── docker-compose.yml
├── start.bat                   # Запуск Windows
├── start.sh                    # Запуск Linux/macOS
└── README.md
```

## 📝 Полезные команды

```bash
# Запуск
docker-compose up --build

# Запуск в фоне
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend

# Статус
docker-compose ps

# Перезапуск
docker-compose restart

# Пересборка
docker-compose build --no-cache
```

## 🧪 Тестирование

### Проверка Ollama

```bash
# Список моделей
ollama list

# Тест модели
ollama run gemma3:1b "Hello"

# API тест
curl http://localhost:11434/api/tags
```

### Проверка Backend

```bash
# Тест главной страницы
curl http://localhost:5000
```

### Проверка Frontend

```bash
# Тест главной страницы
curl http://localhost:3000
```

## 🎨 Дизайн

Современный минималистичный интерфейс:
- **Шрифт**: Inter
- **Цвета**: #2563EB (синий), #7C3AED (фиолетовый), #F5F7FA (фон)
- **Особенности**: Карточки с тенями, скруглённые углы, плавные анимации
- **Анимация**: Котик-аналитик печатает на ноутбуке во время AI-анализа 🐱💻

## 🔒 Безопасность

- ✅ Все данные обрабатываются локально
- ✅ Нет отправки данных в облако
- ✅ Нет API ключей
- ✅ Нет внешних зависимостей

## 📊 Производительность

### Оптимизации

- Ленивая загрузка таблиц (по 100 строк)
- Обработка только первых 15 строк для LLM
- Кэширование статики в Nginx
- Компактная модель gemma3:1b (815MB)

### Рекомендации

- Для больших файлов используйте CSV вместо Excel
- Для лучшего качества анализа используйте llama3:8b
- Для максимальной скорости используйте gemma3:1b

## 🚧 Расширение

### Добавление нового типа файлов

1. Обновите `ALLOWED_EXTENSIONS` в `app.py`
2. Добавьте парсер в `read_data_file()`
3. Обновите `accept` в HTML

### Добавление нового API endpoint

1. Добавьте route в `app.py`
2. Добавьте проксирование в `frontend/nginx.conf`
3. Вызовите из `static/script.js`

## 🤝 Вклад

Pull requests приветствуются!

## 📄 Лицензия

MIT

## 💡 Особенности реализации

### Почему Ollama локально, а не в Docker?

- Docker образ Ollama (3.35GB) слишком большой для Windows
- Локальная установка быстрее и стабильнее
- Backend подключается через `host.docker.internal:11434`
- Можно легко менять модели без пересборки контейнеров

### Почему gemma3:1b?

- Компактная (815MB)
- Быстрая (анализ за 10-20 секунд)
- Достаточно точная для базового анализа
- Работает на слабых машинах (2GB RAM)

## 🎯 Roadmap

- [ ] Поддержка JSON файлов
- [ ] Экспорт в Excel
- [ ] Сохранение истории анализов
- [ ] Сравнение нескольких файлов
- [ ] Настройка промптов через UI
- [ ] Поддержка других LLM (OpenAI, Anthropic)

---

**Сделано с ❤️ для локальной аналитики**

🐱 *P.S. Котик-аналитик работает усердно!*
