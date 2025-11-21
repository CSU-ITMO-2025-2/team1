"""Модель данных для для парсинга резюме"""

from typing import List
from pydantic import BaseModel, Field

class ParsedResumeSkills(BaseModel):
    """
    Модель для хранения навыков, извлеченных из вакансии
    
    Attributes:
        skills (List[str]): Навыки из резюме
    """
    skills: List[str] = Field(default_factory=list, description="Навыки из резюме")