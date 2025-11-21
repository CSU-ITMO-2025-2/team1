"""Модель данных для определения релевантности навыков"""

from typing import List, Literal

from pydantic import BaseModel, Field, create_model


def create_pydantic_skills_relevance_matching_model(
    unmatched_vac_list: list, unmatched_res_list: list
):
    """
    Создает динамическую модель для определения релевантности навыка
    
    Attributes:
        vacancy_skill: Навык из вакансии
        resume_skill: Навык из резюме
        reason: Причина релевантности
        relevance_category: Категория релевантности
    """
    unmatched_vac_skills_literal = Literal[tuple(unmatched_vac_list)]
    unmatched_res_skills_literal = Literal[tuple(unmatched_res_list)]

    relevance_category = [
        "Полная аналогичность",
        "Частичная аналогичность",
        "Отсутствует аналогичность",
    ]

    relevance_category_literal = Literal[tuple(relevance_category)]

    # reason_list = [
    #     "Аналогичный инструмент/технология/процесс", # Полная релевантность
    #     "Отсутствует релевантность", # Нет релевантности
    #     "Схожий процесс", # Частичная релевантность
    #     "Поддержка ключевого процесса" # Частичная релевантность
    # ]

    # reason_list_literal = Literal[tuple(reason_list)]

    RelevancedSkills = create_model(
        "RelevancedSkills",
        vacancy_skill=(
            unmatched_vac_skills_literal,
            Field(..., description="Навык из вакансии"),
        ),
        resume_skill=(
            unmatched_res_skills_literal,
            Field(..., description="Навык из резюме"),
        ),
        reason=(
            str,
            Field(
                ...,
                description="Краткое обоснование выбора категории аналогичности, используй для коротких размышлений по выбору категории",
            ),
        ),
        relevance=(
            relevance_category_literal,
            Field(
                ...,
                description="Категория аналогичности, к которой можно отнести навык из резюме по отношению к навыку из вакансии",
            ),
        ),
    )

    class RelevancedSkillsList(BaseModel):
        """
        Список навыков с проставленной категорией релевантности
        
        Attributes:
            pairs: Список навыков с проставленной категорией релевантности
        """
        pairs: List[RelevancedSkills] = Field(
            ..., description="Список навыков с проставленной категорией релевантности"
        )

    return RelevancedSkillsList
