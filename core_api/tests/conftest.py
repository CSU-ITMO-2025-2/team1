"""
Конфигурация pytest и общие fixtures для тестов Core API.
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.api.dependencies import get_rabbit_client

from app.core.config import settings
from app.db import get_session
from app.main import app
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_DATABASE_URL = settings.postgres.url


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создает event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db_engine():
    """Создает тестовый движок БД (использует продовую БД)."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Создает тестовую сессию БД с транзакцией.
    Все изменения откатываются после теста.
    """
    # Создаем соединение
    async with test_db_engine.connect() as connection:
        # Начинаем транзакцию
        transaction = await connection.begin()

        # Создаем сессию с этим соединением
        async_session_maker = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        async with async_session_maker() as session:
            yield session

            # Откатываем транзакцию после теста
            await transaction.rollback()


@pytest.fixture
def mock_rabbit_client():
    """Мок RabbitMQ клиента."""
    mock_client = MagicMock()

    # Мокаем метод call для возврата успешных ответов
    async def mock_call(payload, queue_name):
        if queue_name == "resume_evaluation_task":
            return {
                "status": "success",
                "data": {
                    "salary_evaluation": {"match": "good"},
                    "education_evaluation": {"match": "good"},
                    "additional_evaluation": {"match": "good"},
                    "work_experience_report": {"match": "good"},
                    "skills_report": {"match": "good"},
                },
            }
        elif queue_name == "job_description_task":
            return {
                "status": "success",
                "data": {
                    "job_site": "Test job description",
                    "job_flyer_format": "Test flyer",
                    "job_media_format": "Test media",
                    "job_social_media_format": "Test social",
                },
            }
        elif queue_name == "question_generation_task":
            return {
                "status": "success",
                "data": {
                    "experience": {"questions": ["Q1", "Q2"]},
                    "motivation": {"questions": ["Q3", "Q4"]},
                    "personal": {"questions": ["Q5", "Q6"]},
                },
            }
        return {"status": "error", "message": "Unknown queue"}

    mock_client.call = AsyncMock(side_effect=mock_call)
    mock_client.connection = MagicMock()
    mock_client.connection.is_closed = False

    return mock_client


@pytest.fixture
def test_client(test_db_session, mock_rabbit_client):
    """Создает тестовый клиент FastAPI с подменой зависимостей."""

    # Переопределяем зависимости
    async def override_get_session():
        yield test_db_session

    def override_get_rabbit_client():
        return mock_rabbit_client

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_rabbit_client] = override_get_rabbit_client

    with TestClient(app) as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture
async def async_test_client(test_db_session, mock_rabbit_client):
    """Создает асинхронный тестовый клиент."""
    from httpx import ASGITransport

    # Переопределяем зависимости
    async def override_get_session():
        yield test_db_session

    def override_get_rabbit_client():
        return mock_rabbit_client

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_rabbit_client] = override_get_rabbit_client

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Пример данных пользователя."""
    return {"email": "test@example.com", "full_name": "Test User"}


@pytest.fixture
def sample_resume_text():
    """Пример текста резюме."""
    return """
    Иван Иванов
    Backend разработчик
    Опыт: 3 года
    Навыки: Python, FastAPI, PostgreSQL
    Email: ivan@example.com
    """


@pytest.fixture
def sample_vacancy_text():
    """Пример текста вакансии."""
    return """
    Требуется Backend разработчик
    Опыт: от 2 лет
    Технологии: Python, FastAPI, Docker
    Зарплата: 150000-200000 руб
    """


# ==================== Auth Mocking Fixtures ====================


@pytest.fixture
def mock_keycloak_user():
    """Мок данных пользователя из Keycloak."""
    return {
        "sub": "test-user-id-123",
        "email": "test@example.com",
        "name": "Test User",
        "preferred_username": "testuser",
        "groups": ["админ", "рекрутер"],
        "email_verified": True,
    }


@pytest.fixture
def mock_auth_service_success(mock_keycloak_user):
    """
    Мок успешного ответа от auth_service.

    Использование:
        with mock_auth_service_success():
            # Ваш тест здесь
    """

    async def mock_get(*args, **kwargs):
        """Мок httpx.AsyncClient.get для auth_service."""
        response = MagicMock(spec=Response)
        response.status_code = 200
        response.json.return_value = mock_keycloak_user
        response.raise_for_status = MagicMock()
        return response

    return patch("httpx.AsyncClient.get", new=mock_get)


@pytest.fixture
def mock_auth_service_unauthorized():
    """
    Мок неавторизованного ответа от auth_service (401).

    Использование:
        with mock_auth_service_unauthorized():
            # Ваш тест здесь
    """

    async def mock_get(*args, **kwargs):
        """Мок httpx.AsyncClient.get для auth_service."""
        response = MagicMock(spec=Response)
        response.status_code = 401
        response.json.return_value = {"error": "unauthorized"}
        return response

    return patch("httpx.AsyncClient.get", new=mock_get)


@pytest.fixture
def mock_auth_service_error():
    """
    Мок ошибки при обращении к auth_service.

    Использование:
        with mock_auth_service_error():
            # Ваш тест здесь
    """

    async def mock_get(*args, **kwargs):
        """Мок httpx.AsyncClient.get для auth_service."""
        from httpx import HTTPError

        raise HTTPError("Connection error")

    return patch("httpx.AsyncClient.get", new=mock_get)


@pytest.fixture
def override_auth_optional(mock_keycloak_user):
    """
    Переопределяет get_user_data для возврата тестового пользователя.
    Используется для тестов с опциональной авторизацией.
    """
    from app.api.dependencies import get_user_data
    from app.api.schemas.common import UserData

    async def mock_get_user_data():
        # Преобразуем данные Keycloak в UserData
        return UserData(
            email=mock_keycloak_user.get("email"),
            full_name=mock_keycloak_user.get("name")
            or mock_keycloak_user.get("preferred_username"),
        )

    app.dependency_overrides[get_user_data] = mock_get_user_data
    yield
    app.dependency_overrides.pop(get_user_data, None)


@pytest.fixture
def override_auth_none():
    """
    Переопределяет get_user_data для возврата None (неавторизованный пользователь).
    Используется для тестов без авторизации.
    """
    from app.api.dependencies import get_user_data

    async def mock_get_user_data():
        return None

    app.dependency_overrides[get_user_data] = mock_get_user_data
    yield
    app.dependency_overrides.pop(get_user_data, None)


@pytest.fixture
def test_client_with_auth(test_db_session, mock_rabbit_client, override_auth_optional):
    """
    Создает тестовый клиент FastAPI с авторизованным пользователем.
    """

    # Переопределяем зависимости
    async def override_get_session():
        yield test_db_session

    def override_get_rabbit_client():
        return mock_rabbit_client

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_rabbit_client] = override_get_rabbit_client

    with TestClient(app) as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture
def test_client_no_auth(test_db_session, mock_rabbit_client, override_auth_none):
    """
    Создает тестовый клиент FastAPI без авторизации.
    """

    # Переопределяем зависимости
    async def override_get_session():
        yield test_db_session

    def override_get_rabbit_client():
        return mock_rabbit_client

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_rabbit_client] = override_get_rabbit_client

    with TestClient(app) as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()
