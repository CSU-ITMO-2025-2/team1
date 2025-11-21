"""Модель данных для извлечения и классификации навыков из вакансии"""

from typing import List

from pydantic import BaseModel, Field


class ParsedJobSkills(BaseModel):
    """
    Модель для хранения навыков, извлеченных из вакансии, по категориям
    
    Attributed:
        must_have_skills (List[str]): Обязательные навыки
        nice_to_have_skills (List[str]): Желательные навыки
    """

    must_have_skills: List[str] = Field(
        default_factory=list, description="Обязательные навыки"
    )
    nice_to_have_skills: List[str] = Field(
        default_factory=list, description="Желательные навыки"
    )
