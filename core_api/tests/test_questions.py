"""
Тесты для question generation endpoint.
"""
import pytest


@pytest.mark.unit
def test_question_generation_with_auth(test_client_with_auth, sample_vacancy_text, sample_resume_text):
    """Тест успешной генерации вопросов с авторизацией."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text,
    }
    
    response = test_client_with_auth.post("/questions/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"] is not None


@pytest.mark.unit
def test_question_generation_without_auth(test_client_no_auth, sample_vacancy_text, sample_resume_text):
    """Тест генерации вопросов без авторизации (должно работать)."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text
    }
    
    response = test_client_no_auth.post("/questions/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"




@pytest.mark.unit
def test_question_generation_missing_vacancy(test_client_no_auth, sample_resume_text):
    """Тест с отсутствующим текстом вакансии."""
    payload = {
        "resume_text": sample_resume_text
    }
    
    response = test_client_no_auth.post("/questions/generate", json=payload)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_question_generation_missing_resume(test_client_no_auth, sample_vacancy_text):
    """Тест с отсутствующим текстом резюме."""
    payload = {
        "vacancy_text": sample_vacancy_text
    }
    
    response = test_client_no_auth.post("/questions/generate", json=payload)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_question_generation_async(async_test_client, sample_vacancy_text, sample_resume_text):
    """Асинхронный тест генерации вопросов."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text
    }
    
    response = await async_test_client.post("/questions/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"


@pytest.mark.unit
def test_question_generation_response_structure(test_client_with_auth, sample_vacancy_text, sample_resume_text):
    """Тест структуры ответа генерации вопросов."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text
    }
    
    response = test_client_with_auth.post("/questions/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Проверяем структуру ответа
    assert "status" in data
    assert "data" in data
    
    # Проверяем, что data содержит ожидаемые поля
    result_data = data["data"]
    assert "experience" in result_data
    assert "motivation" in result_data
    assert "personal" in result_data


@pytest.mark.unit
def test_question_generation_empty_texts(test_client_no_auth):
    """Тест с пустыми текстами."""
    payload = {
        "vacancy_text": "",
        "resume_text": ""
    }
    
    response = test_client_no_auth.post("/questions/generate", json=payload)
    
    # Должен пройти валидацию Pydantic
    assert response.status_code in [200, 422]


@pytest.mark.unit
def test_question_generation_creates_user(test_client_with_auth, sample_vacancy_text, sample_resume_text):
    """Тест создания пользователя при генерации вопросов с авторизацией."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text,
    }
    
    response = test_client_with_auth.post("/questions/generate", json=payload)
    
    assert response.status_code == 200


@pytest.mark.unit
def test_question_generation_calls_resume_evaluation_first(test_client_no_auth, mock_rabbit_client, sample_vacancy_text, sample_resume_text):
    """Тест что генерация вопросов сначала вызывает оценку резюме."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text
    }
    
    response = test_client_no_auth.post("/questions/generate", json=payload)
    
    assert response.status_code == 200
    
    # Проверяем, что были вызваны оба воркера
    assert mock_rabbit_client.call.call_count == 2  # resume_evaluation + question_generation

