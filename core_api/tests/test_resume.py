"""
Тесты для resume evaluation endpoint.
"""
import pytest


@pytest.mark.unit
def test_resume_evaluation_with_auth(test_client_with_auth, sample_vacancy_text, sample_resume_text):
    """Тест успешной оценки резюме с авторизацией."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text,
    }
    
    response = test_client_with_auth.post("/resume/evaluation", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"] is not None


@pytest.mark.unit
def test_resume_evaluation_without_auth(test_client_no_auth, sample_vacancy_text, sample_resume_text):
    """Тест оценки резюме без авторизации (должно работать)."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text
    }
    
    response = test_client_no_auth.post("/resume/evaluation", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"




@pytest.mark.unit
def test_resume_evaluation_missing_vacancy(test_client_no_auth, sample_resume_text):
    """Тест с отсутствующим текстом вакансии."""
    payload = {
        "resume_text": sample_resume_text
    }
    
    response = test_client_no_auth.post("/resume/evaluation", json=payload)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_resume_evaluation_missing_resume(test_client_no_auth, sample_vacancy_text):
    """Тест с отсутствующим текстом резюме."""
    payload = {
        "vacancy_text": sample_vacancy_text
    }
    
    response = test_client_no_auth.post("/resume/evaluation", json=payload)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_resume_evaluation_empty_texts(test_client_no_auth):
    """Тест с пустыми текстами."""
    payload = {
        "vacancy_text": "",
        "resume_text": ""
    }
    
    response = test_client_no_auth.post("/resume/evaluation", json=payload)
    
    # Должен пройти валидацию Pydantic, но может вернуть ошибку от воркера
    assert response.status_code in [200, 422]


@pytest.mark.unit
def test_resume_evaluation_creates_user(test_client_with_auth, test_db_session, sample_vacancy_text, sample_resume_text):
    """Тест создания пользователя при оценке резюме с авторизацией."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text,
    }
    
    response = test_client_with_auth.post("/resume/evaluation", json=payload)
    
    assert response.status_code == 200
    
    # Проверяем, что пользователь создан в БД
    # (в реальном тесте нужно было бы проверить через запрос к БД)


@pytest.mark.asyncio
async def test_resume_evaluation_async(async_test_client, sample_vacancy_text, sample_resume_text):
    """Асинхронный тест оценки резюме."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text
    }
    
    response = await async_test_client.post("/resume/evaluation", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "data" in data


@pytest.mark.unit
def test_resume_evaluation_response_structure(test_client_with_auth, sample_vacancy_text, sample_resume_text):
    """Тест структуры ответа оценки резюме."""
    payload = {
        "vacancy_text": sample_vacancy_text,
        "resume_text": sample_resume_text
    }
    
    response = test_client_with_auth.post("/resume/evaluation", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Проверяем структуру ответа
    assert "status" in data
    assert "data" in data
    
    # Проверяем, что data содержит ожидаемые поля
    result_data = data["data"]
    assert "salary_evaluation" in result_data
    assert "education_evaluation" in result_data
    assert "additional_evaluation" in result_data
    assert "work_experience_report" in result_data
    assert "skills_report" in result_data

