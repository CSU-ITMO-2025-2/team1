"""
Тесты для job description generation endpoint.
"""

import pytest


@pytest.mark.unit
def test_job_description_generation_with_auth(test_client_with_auth):
    """Тест успешной генерации описания вакансии с авторизацией."""
    payload = {
        "input_data": "Python разработчик, опыт 3 года, FastAPI, PostgreSQL",
    }

    response = test_client_with_auth.post("/job_description/generate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "data" in data
    assert data["data"] is not None


@pytest.mark.unit
def test_job_description_without_auth(test_client_no_auth):
    """Тест генерации описания вакансии без авторизации (должно работать)."""
    payload = {"input_data": "Python разработчик, FastAPI"}

    response = test_client_no_auth.post("/job_description/generate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"


@pytest.mark.unit
def test_job_description_missing_input(test_client_no_auth):
    """Тест с отсутствующими входными данными."""
    payload = {}

    response = test_client_no_auth.post("/job_description/generate", json=payload)

    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_job_description_empty_input(test_client_no_auth):
    """Тест с пустыми входными данными."""
    payload = {"input_data": ""}

    response = test_client_no_auth.post("/job_description/generate", json=payload)

    # Должен пройти валидацию Pydantic
    assert response.status_code in [422]


@pytest.mark.asyncio
async def test_job_description_async(async_test_client):
    """Асинхронный тест генерации описания вакансии."""
    payload = {"input_data": "Python разработчик, FastAPI, Docker"}

    response = await async_test_client.post("/job_description/generate", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"


@pytest.mark.unit
def test_job_description_response_structure(test_client_with_auth):
    """Тест структуры ответа генерации описания вакансии."""
    payload = {"input_data": "Backend разработчик, Python, FastAPI"}

    response = test_client_with_auth.post("/job_description/generate", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Проверяем структуру ответа
    assert "status" in data
    assert "data" in data

    # Проверяем, что data содержит ожидаемые поля
    result_data = data["data"]
    assert "job_site" in result_data
    assert "job_flyer_format" in result_data
    assert "job_media_format" in result_data
    assert "job_social_media_format" in result_data


@pytest.mark.unit
def test_job_description_special_characters(test_client_no_auth):
    """Тест с специальными символами во входных данными."""
    payload = {
        "input_data": "Python разработчик! @#$%^&*() <script>alert('test')</script>"
    }

    response = test_client_no_auth.post("/job_description/generate", json=payload)

    assert response.status_code == 200


@pytest.mark.unit
def test_job_description_unicode(test_client_no_auth):
    """Тест с unicode символами."""
    payload = {"input_data": "Python разработчик 🐍 с опытом работы с FastAPI ⚡"}

    response = test_client_no_auth.post("/job_description/generate", json=payload)

    assert response.status_code == 200


@pytest.mark.unit
async def test_job_description_creates_user_in_db(
    test_client_with_auth, test_db_session, mock_keycloak_user
):
    """Тест что пользователь создается в БД при авторизации."""
    from app.db.models import User
    from sqlalchemy import select

    payload = {"input_data": "Python разработчик"}

    response = test_client_with_auth.post("/job_description/generate", json=payload)

    assert response.status_code == 200

    # Проверяем, что пользователь создан в БД
    result = await test_db_session.execute(
        select(User).where(User.email == mock_keycloak_user["email"])
    )
    user = result.scalar_one_or_none()

    assert user is not None, "Пользователь должен быть создан в БД"
    assert user.email == mock_keycloak_user["email"]
    assert user.full_name == mock_keycloak_user["name"]


@pytest.mark.unit
async def test_job_description_saves_full_input_data(
    test_client_with_auth, test_db_session
):
    """Тест что полный текст входных данных сохраняется в БД."""
    from app.db.models import GenerationResult
    from sqlalchemy import select

    input_text = "Python разработчик с опытом работы 5 лет в FastAPI и PostgreSQL"
    payload = {"input_data": input_text}

    response = test_client_with_auth.post("/job_description/generate", json=payload)

    assert response.status_code == 200

    # Проверяем, что в БД сохранен полный текст
    result = await test_db_session.execute(
        select(GenerationResult)
        .where(GenerationResult.request_type == "job_description")
        .order_by(GenerationResult.created_at.desc())
        .limit(1)
    )
    generation_result = result.scalar_one_or_none()

    assert generation_result is not None, "Результат должен быть сохранен в БД"
    assert generation_result.request_payload is not None
    assert "input_data" in generation_result.request_payload
    assert generation_result.request_payload["input_data"] == input_text, (
        "Полный текст входных данных должен быть сохранен в request_payload"
    )
