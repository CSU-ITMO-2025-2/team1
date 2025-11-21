"""
Тесты для репозиториев.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, GenerationResult
from app.repositories import UserRepository, GenerationResultRepository


@pytest.mark.asyncio
class TestUserRepository:
    """Тесты для UserRepository."""
    
    async def test_get_by_id(self, session: AsyncSession, sample_user: User):
        """Тест получения пользователя по ID."""
        repo = UserRepository(session)
        user = await repo.get_by_id(sample_user.id)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email
    
    async def test_get_by_id_not_found(self, session: AsyncSession):
        """Тест получения несуществующего пользователя по ID."""
        repo = UserRepository(session)
        user = await repo.get_by_id(99999)
        
        assert user is None
    
    async def test_get_by_provider_id(self, session: AsyncSession, sample_user: User):
        """Тест получения пользователя по провайдеру и external_id."""
        repo = UserRepository(session)
        user = await repo.get_by_provider_id(
            sample_user.auth_provider,
            sample_user.external_id
        )
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.external_id == sample_user.external_id
    
    async def test_get_by_provider_id_not_found(self, session: AsyncSession):
        """Тест получения несуществующего пользователя по провайдеру."""
        repo = UserRepository(session)
        user = await repo.get_by_provider_id("unknown", "unknown_id")
        
        assert user is None
    
    async def test_get_by_email(self, session: AsyncSession, sample_user: User):
        """Тест получения пользователя по email."""
        repo = UserRepository(session)
        user = await repo.get_by_email(sample_user.email)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email
    
    async def test_create_user(self, session: AsyncSession):
        """Тест создания нового пользователя."""
        repo = UserRepository(session)
        user = await repo.create(
            auth_provider="keycloak",
            external_id="new_user_123",
            email="newuser@example.com",
            full_name="Новый Пользователь",
        )
        
        assert user.id is not None
        assert user.auth_provider == "keycloak"
        assert user.external_id == "new_user_123"
        assert user.email == "newuser@example.com"
        assert user.full_name == "Новый Пользователь"
    
    async def test_get_or_create_existing_user(
        self,
        session: AsyncSession,
        sample_user: User
    ):
        """Тест получения существующего пользователя через get_or_create."""
        repo = UserRepository(session)
        user, created = await repo.get_or_create_by_provider_id(
            auth_provider=sample_user.auth_provider,
            external_id=sample_user.external_id,
            email="different@example.com",  # Другой email
        )
        
        assert user.id == sample_user.id
        assert created is False
        # Email не должен измениться
        assert user.email == sample_user.email
    
    async def test_get_or_create_new_user(self, session: AsyncSession):
        """Тест создания нового пользователя через get_or_create."""
        repo = UserRepository(session)
        user, created = await repo.get_or_create_by_provider_id(
            auth_provider="internal",
            external_id="brand_new_user",
            email="brandnew@example.com",
            full_name="Совсем Новый",
        )
        
        assert user.id is not None
        assert created is True
        assert user.auth_provider == "internal"
        assert user.external_id == "brand_new_user"
        assert user.email == "brandnew@example.com"
    
    async def test_update_user(self, session: AsyncSession, sample_user: User):
        """Тест обновления данных пользователя."""
        repo = UserRepository(session)
        updated_user = await repo.update(
            user_id=sample_user.id,
            email="updated@example.com",
            full_name="Обновлённое Имя",
        )
        
        assert updated_user is not None
        assert updated_user.id == sample_user.id
        assert updated_user.email == "updated@example.com"
        assert updated_user.full_name == "Обновлённое Имя"
    
    async def test_update_nonexistent_user(self, session: AsyncSession):
        """Тест обновления несуществующего пользователя."""
        repo = UserRepository(session)
        updated_user = await repo.update(
            user_id=99999,
            email="test@example.com",
        )
        
        assert updated_user is None


@pytest.mark.asyncio
class TestGenerationResultRepository:
    """Тесты для GenerationResultRepository."""
    
    async def test_get_by_id(
        self,
        session: AsyncSession,
        sample_generation_result: GenerationResult
    ):
        """Тест получения результата генерации по ID."""
        repo = GenerationResultRepository(session)
        result = await repo.get_by_id(sample_generation_result.id)
        
        assert result is not None
        assert result.id == sample_generation_result.id
        assert result.request_type == sample_generation_result.request_type
    
    async def test_create_generation_result(
        self,
        session: AsyncSession,
        sample_user: User
    ):
        """Тест создания результата генерации."""
        repo = GenerationResultRepository(session)
        result = await repo.create(
            request_type="job_description",
            status="success",
            user_id=sample_user.id,
            request_payload={"input": "data"},
            response_payload={"output": "result"},
            model_name="gpt-4",
            tokens_input=100,
            tokens_output=200,
            latency_ms=1500,
        )
        
        assert result.id is not None
        assert result.user_id == sample_user.id
        assert result.request_type == "job_description"
        assert result.status == "success"
        assert result.latency_ms == 1500
    
    async def test_create_anonymous_result(self, session: AsyncSession):
        """Тест создания результата для анонимного пользователя."""
        repo = GenerationResultRepository(session)
        result = await repo.create(
            request_type="resume_evaluation",
            status="success",
            user_id=None,  # Анонимный
        )
        
        assert result.id is not None
        assert result.user_id is None
    
    async def test_get_by_user_id(
        self,
        session: AsyncSession,
        sample_user: User,
        sample_generation_result: GenerationResult
    ):
        """Тест получения результатов по user_id."""
        repo = GenerationResultRepository(session)
        results = await repo.get_by_user_id(sample_user.id)
        
        assert len(results) > 0
        assert all(r.user_id == sample_user.id for r in results)
    
    async def test_get_by_request_type(
        self,
        session: AsyncSession,
        sample_generation_result: GenerationResult
    ):
        """Тест получения результатов по типу запроса."""
        repo = GenerationResultRepository(session)
        results = await repo.get_by_request_type("resume_evaluation")
        
        assert len(results) > 0
        assert all(r.request_type == "resume_evaluation" for r in results)
    
    async def test_get_by_user_and_type(
        self,
        session: AsyncSession,
        sample_user: User,
        sample_generation_result: GenerationResult
    ):
        """Тест получения результатов по user_id и типу запроса."""
        repo = GenerationResultRepository(session)
        results = await repo.get_by_user_and_type(
            sample_user.id,
            "resume_evaluation"
        )
        
        assert len(results) > 0
        assert all(
            r.user_id == sample_user.id and r.request_type == "resume_evaluation"
            for r in results
        )
    
    async def test_get_statistics_by_user(
        self,
        session: AsyncSession,
        sample_user: User
    ):
        """Тест получения статистики по пользователю."""
        repo = GenerationResultRepository(session)
        
        # Создаём несколько результатов разных типов
        await repo.create(
            request_type="job_description",
            status="success",
            user_id=sample_user.id,
        )
        await repo.create(
            request_type="job_description",
            status="success",
            user_id=sample_user.id,
        )
        await repo.create(
            request_type="resume_evaluation",
            status="success",
            user_id=sample_user.id,
        )
        
        stats = await repo.get_statistics_by_user(sample_user.id)
        
        assert "job_description" in stats
        assert "resume_evaluation" in stats
        assert stats["job_description"] == 2
        assert stats["resume_evaluation"] >= 1  # Включая sample_generation_result

