"""
Тесты для ORM моделей.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, GenerationResult


@pytest.mark.asyncio
class TestUserModel:
    """Тесты для модели User."""
    
    async def test_create_user(self, session: AsyncSession):
        """Тест создания пользователя."""
        user = User(
            auth_provider="keycloak",
            external_id="user123",
            email="user@example.com",
            full_name="Иван Иванов",
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.auth_provider == "keycloak"
        assert user.external_id == "user123"
        assert user.email == "user@example.com"
        assert user.full_name == "Иван Иванов"
        assert user.created_at is not None
        assert user.updated_at is not None
    
    async def test_user_unique_constraint(self, session: AsyncSession):
        """Тест уникальности (auth_provider, external_id)."""
        user1 = User(
            auth_provider="keycloak",
            external_id="user123",
            email="user1@example.com",
        )
        session.add(user1)
        await session.commit()
        
        # Попытка создать пользователя с такими же provider и external_id
        user2 = User(
            auth_provider="keycloak",
            external_id="user123",
            email="user2@example.com",
        )
        session.add(user2)
        
        with pytest.raises(Exception):  # Ожидаем ошибку уникальности
            await session.commit()
    
    async def test_user_optional_fields(self, session: AsyncSession):
        """Тест создания пользователя без опциональных полей."""
        user = User(
            auth_provider="internal",
            external_id="user456",
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.email is None
        assert user.full_name is None
    
    async def test_user_str_representation(self, sample_user: User):
        """Тест строкового представления пользователя."""
        str_repr = repr(sample_user)
        
        assert "User" in str_repr
        assert str(sample_user.id) in str_repr
        assert sample_user.auth_provider in str_repr
        assert sample_user.external_id in str_repr


@pytest.mark.asyncio
class TestGenerationResultModel:
    """Тесты для модели GenerationResult."""
    
    async def test_create_generation_result(
        self,
        session: AsyncSession,
        sample_user: User
    ):
        """Тест создания результата генерации."""
        result = GenerationResult(
            user_id=sample_user.id,
            request_type="job_description",
            request_payload={"input": "test"},
            response_payload={"output": "result"},
            model_name="gpt-4",
            status="success",
            tokens_input=50,
            tokens_output=150,
            latency_ms=2000,
        )
        
        session.add(result)
        await session.commit()
        await session.refresh(result)
        
        assert result.id is not None
        assert result.user_id == sample_user.id
        assert result.request_type == "job_description"
        assert result.request_payload == {"input": "test"}
        assert result.response_payload == {"output": "result"}
        assert result.model_name == "gpt-4"
        assert result.status == "success"
        assert result.tokens_input == 50
        assert result.tokens_output == 150
        assert result.latency_ms == 2000
        assert result.created_at is not None
    
    async def test_create_anonymous_generation_result(self, session: AsyncSession):
        """Тест создания результата генерации для анонимного пользователя."""
        result = GenerationResult(
            user_id=None,  # Анонимный запрос
            request_type="resume_evaluation",
            status="success",
        )
        
        session.add(result)
        await session.commit()
        await session.refresh(result)
        
        assert result.id is not None
        assert result.user_id is None
    
    async def test_generation_result_with_error(self, session: AsyncSession):
        """Тест создания результата генерации с ошибкой."""
        result = GenerationResult(
            user_id=None,
            request_type="question_generation",
            status="error",
            error_message="Timeout error",
            latency_ms=5000,
        )
        
        session.add(result)
        await session.commit()
        await session.refresh(result)
        
        assert result.id is not None
        assert result.status == "error"
        assert result.error_message == "Timeout error"
    
    async def test_generation_result_str_representation(
        self,
        sample_generation_result: GenerationResult
    ):
        """Тест строкового представления результата генерации."""
        str_repr = repr(sample_generation_result)
        
        assert "GenerationResult" in str_repr
        assert str(sample_generation_result.id) in str_repr
        assert sample_generation_result.request_type in str_repr
        assert sample_generation_result.status in str_repr
    
    async def test_generation_result_relationship(
        self,
        session: AsyncSession,
        sample_generation_result: GenerationResult
    ):
        """Тест связи между GenerationResult и User."""
        # Загружаем результат из БД
        result = await session.get(GenerationResult, sample_generation_result.id)
        
        # Проверяем, что связь с пользователем работает
        assert result.user is not None
        assert result.user.id == sample_generation_result.user_id
        assert result.user.external_id == "test_external_123"

