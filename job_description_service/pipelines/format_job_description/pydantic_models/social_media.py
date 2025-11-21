"""Модель описания вакансии для социальных сетей"""

from typing import List

from pydantic import BaseModel, Field


class SocialMediaFormat(BaseModel):
    """
    Модель описания вакансии для социальных сетей
    
    Attributes:
        company_info - Вводная информация о компании
        project_info - Описание проекта и задач
        key_requirements - Ключевые требования к кандидату
        hashtags - Хэштеги для поиска
    """

    company_info: str = Field(..., description="Вводная информация о компании")
    project_info: str = Field(..., description="Описание проекта и задач")
    key_requirements: str = Field(..., description="Ключевые требования")
    hashtags: List[str] = Field(..., description="Хэштеги для поиска")
