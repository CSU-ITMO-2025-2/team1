# Core API - HR Assistant

Основной сервис HR-ассистента для оценки резюме, генерации описаний вакансий и вопросов для интервью.

## 🚀 Быстрый старт

```bash
# Установка зависимостей
uv sync

# Запуск сервиса
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или через Docker
docker-compose up core_api
```

## 📚 Документация API

После запуска доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🏗️ Архитектура

```
core_api/
├── app/
│   ├── api/              # API слой
│   │   ├── dependencies.py
│   │   ├── routes/       # Эндпоинты
│   │   └── schemas/      # Pydantic модели
│   ├── services/         # Бизнес-логика
│   ├── repositories/     # Работа с БД
│   ├── middleware/       # Middleware
│   ├── core/            # Конфигурация
│   ├── utils/           # Утилиты
│   └── main.py          # Точка входа
├── entrypoint.sh        # Docker entrypoint
└── Dockerfile           # Docker образ
```

## 🔌 API Эндпоинты

### Health Check
```
GET /health
```

### Оценка резюме
```
POST /resume/evaluation
Content-Type: multipart/form-data

Parameters:
- vacancy_text: str (optional)
- vacancy_file: file (optional)
- resume_text: str (optional)
- resume_file: file (optional)
- user_data: json string (optional)
```

### Генерация описания вакансии
```
POST /job_description/generate
Content-Type: multipart/form-data

Parameters:
- input_data: str (optional)
- input_file: file (optional)
- user_data: json string (optional)
```

### Генерация вопросов для интервью
```
POST /questions/generate
Content-Type: multipart/form-data

Parameters:
- vacancy_text: str (optional)
- vacancy_file: file (optional)
- resume_text: str (optional)
- resume_file: file (optional)
- user_data: json string (optional)
```

## 🔧 Конфигурация

Переменные окружения (`.env`):

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hr_assist
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# RabbitMQ
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
RABBITMQ_DEFAULT_HOST=localhost
RABBITMQ_PORT=5672

# Logging
LOG_LEVEL=INFO
```

## 📦 Зависимости

Основные:
- FastAPI - веб-фреймворк
- SQLAlchemy - ORM для работы с БД
- aio-pika - асинхронный клиент RabbitMQ
- Pydantic - валидация данных
- python-docx - работа с DOCX
- PyMuPDF - работа с PDF

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С покрытием
pytest --cov=app tests/
```

## 📝 Логирование

Логи выводятся в stdout в формате:
```
УРОВЕНЬ | МОДУЛЬ | СООБЩЕНИЕ
```

Уровень логирования настраивается через `LOG_LEVEL` в `.env`.

## 🔄 Миграции БД

```bash
# Создать новую миграцию
./scripts/create_migration.sh "описание изменений"

# Применить миграции
./scripts/init_db.sh

# Сбросить БД (осторожно!)
./scripts/reset_db.sh
```

## 📖 Дополнительная документация

- [Руководство по рефакторингу](REFACTORING_NOTES.md)
- [Руководство по миграции](MIGRATION_GUIDE.md)

## 🤝 Разработка

### Структура сервисов

**FileService** - извлечение текста из файлов  
**UserService** - управление пользователями  
**GenerationService** - генерация через RabbitMQ  
**LoggingService** - логирование в БД

### Добавление нового эндпоинта

1. Создайте роут в `app/api/routes/`
2. При необходимости добавьте сервис в `app/services/`
3. Добавьте схемы в `app/api/schemas/`
4. Подключите роут в `app/main.py`

### Код-стайл

Проект следует PEP 8 и использует:
- Type hints для всех функций
- Docstrings в Google стиле
- Async/await для асинхронных операций

## 📊 Мониторинг

Health check эндпоинт возвращает статус сервиса, RabbitMQ и PostgreSQL:
```json
{
  "status": "healthy",
  "rabbitmq_status": "подключен",
  "db_status": "подключена"
}
```

## 🐛 Отладка

```bash
# Просмотр логов
docker logs -f core_api

# Подключение к контейнеру
docker exec -it core_api bash

# Проверка БД
docker exec -it postgres psql -U postgres -d hr_assist
```

## 📄 Лицензия

Proprietary

## 👥 Команда

HR Assistant Team

---

**Версия**: 1.0.0  
**Последнее обновление**: 23 ноября 2025

