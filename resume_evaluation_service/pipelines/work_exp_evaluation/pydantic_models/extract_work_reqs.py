"""Модель парсинга требований к опыту работы"""

from pydantic import BaseModel, Field

class WorkExpInfo(BaseModel):
    """
    Модель парсинга требований к опыту работы
    
    Attributes:
        work_years - Количество лет необходимого опыта работы
    """
    work_years: int = Field(None, description="Количество лет необходимого опыта работы")