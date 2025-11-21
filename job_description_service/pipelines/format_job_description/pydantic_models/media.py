"""Модель описания вакансии для медиа (газета/ТВ)"""

from pydantic import BaseModel, Field

class MediaFormat(BaseModel):
    """
    Модель описания вакансии для медиа (газета/ТВ)
    
    Attributes:
        job_title: Наименование вакансии
        key_function: Ключевые функции для должности
    """

    job_title: str = Field(..., description="Наименование вакансии")
    key_function: str = Field(..., description="Ключевые функция для должности")
