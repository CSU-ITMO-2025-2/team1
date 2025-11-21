"""Модель данных для генерации софт скиллов по вакансии"""

from typing import List

from pydantic import BaseModel, Field


class GeneratedSoftSkills(BaseModel):
    """
    Модель для генерации soft skills.
    
    Attributes:
        soft_skills (List[str]): Список сгенерированных soft skills для вакансии.
    """

    soft_skills: List[str] = Field(description="Список сгенерированных soft skills")
