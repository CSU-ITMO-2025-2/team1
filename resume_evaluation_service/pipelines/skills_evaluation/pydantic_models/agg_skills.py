"""Модель данных для агрегации и нормализации навыков в вакансии"""

from typing import List

from pydantic import BaseModel


class AggregatedSkills(BaseModel):
    """
    Список агрегированных навыков
    
    Attributes:
        skills (List[str]): Список агрегированных навыков
    """

    skills: List[str]
