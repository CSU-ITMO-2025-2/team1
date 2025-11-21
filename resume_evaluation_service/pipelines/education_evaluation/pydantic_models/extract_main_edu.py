""" Модели данных для обработки информации об образовании"""

from typing import List, Literal

from pydantic import BaseModel, Field

education_levels = [
    "Высшее",
    "Среднее-специальное",
    "Не указано",
]
specialization_categories = [
    "Техническое",
    "Экономическое",
    "Логистическое",
    "Социально-гуманитарное",
    "Юридическое",
    "Творческое",
    "Медицинское",
    "Инженерное",
    "Педагогическое",
    "Другое",
    "Не указано",
]

education_literal = Literal[tuple(education_levels)]
specialization_literal = Literal[tuple(specialization_categories)]


class EducationInfo(BaseModel):
    """
    Информация об образовании из резюме или вакансии
    
    Attributes:
        level (education_literal): Уровень образования
        specialization (List[specialization_literal]): Область специализации
    """
    level: education_literal = Field(..., description="Уровень образования")
    specialization: List[specialization_literal] = Field(
        ..., description="Область специализации"
    )


class EducationList(BaseModel):
    """
    Список информации об образовании
    
    Attributes:
        edu_list (List[EducationInfo]): Список информации об образовании
    """

    edu_list: List[EducationInfo]
