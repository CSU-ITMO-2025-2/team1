"""Модель данных для классификации навыков в вакансии"""

from typing import List, Literal

from pydantic import BaseModel, Field

# Допустимые категории для reason
skill_categories = [
    "Технология/инструмент",
    "Язык программирования",
    "Язык",
    "Стандарт/методология",
    "Деловой навык",
    "Процессный навык",
    "Личностное качество",
    "Субъективная оценка",
    "Расплывчатая формулировка",
    "Требование к образованию",
    "Опыт работы в должности",
]


# Создаем Literal тип из допустимых категорий
skill_category_literal = Literal[tuple(skill_categories)]


class SkillClassification(BaseModel):
    """
    Классификация одного навыка из вакансии.
    
    Attributes:
        skill_name: Название навыка в точности, как в тексте
        category: Категория классификации навыка
    """

    skill_name: str = Field(..., description="Название навыка в точности, как в тексте")
    category: skill_category_literal = Field(
        ..., description="Категория классификации навыка"
    )


class SkillsList(BaseModel):
    """
    Список классифицированных навыков из вакансии
    
    Attributes:
        skills: Список классифицированных навыков
    """

    skills: List[SkillClassification]
