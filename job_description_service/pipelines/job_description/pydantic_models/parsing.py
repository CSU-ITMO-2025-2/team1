"""Модель данных для парсинга вакансии по блокам информации"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ParsedVacancyData(BaseModel):
    """
    Модель данных для парсинга входных данных для описания вакансии.
    Все атрибуты представленны исключительно данными из описания вакансии.

    Attributes:
        position (str): Название должности.
        key_skills (List[str]): Список ключевых навыков, указанных в описании вакансии.
        experience (str): Требуемый опыт работы.
        education (str): Требования к образованию.
        conditions (str): Условия работы (график, офис/удаленка и т.д.).
        other (str): Дополнительная информация (все что не вошло в предыдущие поля).
    """

    position: str = Field(default=None, description="Название должности")

    key_skills: Optional[List[str]] = Field(
        default_factory=list,
        description="Список ключевых навыков, указанных в описании вакансии",
    )

    experience: Optional[str] = Field(default=None, description="Требуемый опыт работы")

    education: Optional[str] = Field(
        default=None, description="Требования к образованию"
    )

    conditions: Optional[str] = Field(
        default=None, description="Условия работы (график, офис/удаленка и т.д.)"
    )

    other: Optional[str] = Field(default=None, description="Дополнительная информация")
