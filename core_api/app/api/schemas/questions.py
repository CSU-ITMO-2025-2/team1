"""Схемы для генерации вопросов для интервью."""
from pydantic import BaseModel, Field
from typing import Optional


class QuestionGenerationRequest(BaseModel):
    """Запрос на генерацию вопросов для интервью."""
    
    vacancy_text: str = Field(
        ...,
        description="Текст вакансии",
        min_length=1
    )
    resume_text: str = Field(
        ...,
        description="Текст резюме",
        min_length=1
    )


class QuestionGenerationResponse(BaseModel):
    """Ответ с результатом генерации вопросов."""
    
    status: str = Field(
        ...,
        description="Статус выполнения (success/error)"
    )
    data: Optional[dict] = Field(
        None,
        description="Данные с сгенерированными вопросами"
    )
    message: Optional[str] = Field(
        None,
        description="Сообщение об ошибке (если status=error)"
    )

