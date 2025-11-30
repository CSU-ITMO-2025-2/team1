"""
Тесты для health check endpoint.
"""

import pytest


@pytest.mark.unit
def test_health_check_success(test_client):
    """Тест успешной проверки здоровья сервиса."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "rabbitmq_status" in data
    assert "db_status" in data


@pytest.mark.unit
def test_health_check_rabbitmq_connected(test_client):
    """Тест проверки статуса RabbitMQ."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # RabbitMQ должен быть подключен (мок)
    assert data["rabbitmq_status"] == "подключен"


@pytest.mark.unit
def test_health_check_db_connected(test_client):
    """Тест проверки статуса БД."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # БД должна быть подключена
    assert data["db_status"] == "подключена"
