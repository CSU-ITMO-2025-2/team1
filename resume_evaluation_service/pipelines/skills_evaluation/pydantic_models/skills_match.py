"""Модель данных для для матчинга навыков"""

from typing import List, Literal

from pydantic import BaseModel, Field, create_model


def create_pydantic_skills_agg_match_model(vacancy_skills: list, agg_skills: list):
    """
    Создает динамическую модель для матчинга навыка

    Attributes:
        original_name : Исходная формулировка навыка
        category : Категория к которой наиболее можно отнести исходный навык
    """

    skillsLiteral = Literal[tuple(agg_skills)]  # собираем Literal на основе списка
    vacancySkillsLiteral = Literal[tuple(vacancy_skills)]

    CategorizedSkill = create_model(
        "CategorizedSkill",
        original_name=(
            vacancySkillsLiteral,
            Field(..., description="Исходная формулировка навыка"),
        ),
        category=(
            skillsLiteral,
            Field(
                ...,
                description="Категория к которой наиболее можно отнести исходный навык",
            ),
        ),
    )

    class CategorizedSkillsList(BaseModel):
        """
        Список сматченных навыков

        Attributes:
            skills : Список навыков с категорией
        """
        skills: List[CategorizedSkill] = Field(
            ..., description="Список навыков с категорией"
        )

    return CategorizedSkillsList
