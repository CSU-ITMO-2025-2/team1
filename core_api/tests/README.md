# Тесты Core API

Набор unit и integration тестов для Core API сервиса.

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Общие fixtures и конфигурация
├── test_health.py           # Тесты health check endpoint
├── test_resume.py           # Тесты оценки резюме
├── test_job_description.py  # Тесты генерации описания вакансии
└── test_questions.py        # Тесты генерации вопросов
```

## Запуск тестов

### Все тесты

```bash
cd core_api
uv run pytest
```

### С покрытием кода

```bash
uv run pytest --cov=app --cov-report=html --cov-report=term
```

### Только unit тесты

```bash
uv run pytest -m unit
```

### Только integration тесты

```bash
uv run pytest -m integration
```

### Конкретный файл

```bash
uv run pytest tests/test_health.py
```

### Конкретный тест

```bash
uv run pytest tests/test_health.py::test_health_check_success
```

### С подробным выводом

```bash
uv run pytest -v
```

### С выводом print statements

```bash
uv run pytest -s
```

## Fixtures

### Базовые fixtures (conftest.py)

- `test_db_engine` - Тестовый движок БД (SQLite in-memory)
- `test_db_session` - Тестовая сессия БД
- `mock_rabbit_client` - Мок RabbitMQ клиента
- `test_client` - Синхронный тестовый клиент FastAPI
- `async_test_client` - Асинхронный тестовый клиент
- `sample_user_data` - Пример данных пользователя
- `sample_resume_text` - Пример текста резюме
- `sample_vacancy_text` - Пример текста вакансии

## Покрытие кода

После запуска тестов с флагом `--cov-report=html` отчет будет доступен в `htmlcov/index.html`.

## Маркеры

- `@pytest.mark.unit` - Unit тесты (быстрые, изолированные)
- `@pytest.mark.integration` - Integration тесты (медленные, требуют внешних зависимостей)
- `@pytest.mark.asyncio` - Асинхронные тесты

## Примеры

### Добавление нового теста

```python
import pytest

@pytest.mark.unit
def test_my_endpoint(test_client):
    """Описание теста."""
    response = test_client.get("/my-endpoint")
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### Асинхронный тест

```python
@pytest.mark.asyncio
async def test_my_async_endpoint(async_test_client):
    """Асинхронный тест."""
    response = await async_test_client.post(
        "/my-endpoint",
        json={"data": "test"}
    )
    
    assert response.status_code == 200
```

## CI/CD

Тесты автоматически запускаются в CI/CD pipeline перед деплоем.

## База данных для тестов

**Важно:** Тесты используют **продовую БД** (PostgreSQL из Docker). 

### Перед запуском тестов:

1. Убедитесь, что PostgreSQL запущен:
```bash
docker compose up -d postgres
```

2. Убедитесь, что в `.env` файле указаны правильные параметры подключения к БД

### Изоляция тестов

Каждый тест выполняется в отдельной транзакции, которая откатывается после завершения теста. Это гарантирует:
- Тесты не влияют друг на друга
- Продовые данные не изменяются
- Быстрое выполнение тестов

## Troubleshooting

### Ошибка импорта модулей

Убедитесь, что вы запускаете тесты из директории `core_api`:

```bash
cd core_api
uv run pytest
```

### Ошибки с async тестами

Убедитесь, что установлен `pytest-asyncio`:

```bash
uv pip install pytest-asyncio
```

### Ошибки подключения к БД

Убедитесь, что PostgreSQL запущен и доступен:

```bash
docker compose up -d postgres
# Проверьте, что контейнер работает
docker ps | grep postgres
```

