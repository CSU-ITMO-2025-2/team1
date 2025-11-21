"""Модель оценки релевантности опыта работы кандидата"""

from typing import List, Literal

from pydantic import BaseModel, Field, create_model


def create_pydantic_work_exp_relevance_matching_model(work_list: list):
    """
    Создаёт Pydantic-модель с динамическим `Literal` типом для оценки релевантности опыта работы.
    
    Attributes:
        company_position (str): Компания и позиция кандидата из списка его прошлой работы.
        reason (str): Краткое обоснование, почему опыт кандидата на этой должности релевантен или не релевантен вакансии.
        relevance (bool): Релевантен ли опыт кандидата на этой должности для вакансии.
    """

    work_list_literal = Literal[tuple(work_list)]

    RelevancedWork = create_model(
        "RelevancedWork",
        company_position=(
            work_list_literal,
            Field(
                ...,
                description="Компания и позиция кандидата из списка его прошлой работы",
            ),
        ),
        reason=(
            str,
            Field(
                ...,
                description="Краткое обоснование почему опыт кандидата на этой должности релевантен или не релевантен вакансии",
            ),
        ),
        relevance=(
            bool,
            Field(
                ...,
                description="True - опыт на данной должности релевантен вакансии, False - нерелевантен",
            ),
        ),
    )

    class RelevancedWorkList(BaseModel):
        """
        Модель для хранения списка опыта работы с проставленной релевантностью для вакансии.
        
        Attributes:
            pairs (List[RelevancedWork]): Список опыта работы с проставленной релевантностью для вакансии.
        """
        pairs: List[RelevancedWork] = Field(
            ...,
            description="Список опыта работы с проставленной релевантностью для вакансии",
        )

    return RelevancedWorkList
