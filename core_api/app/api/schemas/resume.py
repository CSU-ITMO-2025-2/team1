"""Схемы для оценки резюме."""
from pydantic import BaseModel, Field
from typing import Optional


class ResumeEvaluationRequest(BaseModel):
    """Запрос на оценку резюме."""
    
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


class ResumeEvaluationResponse(BaseModel):
    """Ответ с результатом оценки резюме."""
    
    status: str = Field(
        ...,
        description="Статус выполнения (success/error)"
    )
    data: Optional[dict] = Field(
        None,
        description="Данные результата оценки"
    )
    message: Optional[str] = Field(
        None,
        description="Сообщение об ошибке (если status=error)"
    )

