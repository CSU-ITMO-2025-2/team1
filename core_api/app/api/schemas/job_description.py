"""Схемы для генерации описаний вакансий."""
from pydantic import BaseModel, Field
from typing import Optional


class JobDescriptionRequest(BaseModel):
    """Запрос на генерацию описания вакансии."""
    
    input_data: str = Field(
        ...,
        description="Входные данные для генерации описания вакансии",
        min_length=1
    )


class JobDescriptionResponse(BaseModel):
    """Ответ с результатом генерации описания вакансии."""
    
    status: str = Field(
        ...,
        description="Статус выполнения (success/error)"
    )
    data: Optional[dict] = Field(
        None,
        description="Данные с описаниями вакансии (job_site, job_flyer_format, job_media_format, job_social_media_format)"
    )
    message: Optional[str] = Field(
        None,
        description="Сообщение об ошибке (если status=error)"
    )

