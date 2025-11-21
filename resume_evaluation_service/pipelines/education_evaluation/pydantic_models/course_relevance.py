""""Модель для оценки релевантности курсов"""

from typing import List, Literal

from pydantic import BaseModel, Field, create_model


def create_relevance_course_model(course_names: list[str]) -> type[BaseModel]:
    """
    Создаёт Pydantic-модель с динамическим `Literal` типом для оценки релевантности курса.
    
    Attributes:
        course_name (str): Название курса.
        reason (str): Краткое обоснование, почему курс релевантен/нерелевантен.
        relevance (bool): Релевантен ли курс для вакансии.
    """
    CourseLiteral = Literal[tuple(course_names)]

    return create_model(
        "RelevanceCourse",
        course_name=(CourseLiteral, Field(..., description="Название курса")),
        reason=(
            str,
            Field(
                ...,
                description="Краткое обоснование, почему курс релевантен/нерелевантен",
            ),
        ),
        relevance=(bool, Field(..., description="Релевантен ли курс для вакансии")),
    )


def create_relevance_course_list_model(course_names: list[str]) -> type[BaseModel]:
    """
    Создаёт динамическую модель списка курсов с релевантностью. 
    
    Attributes:
        courses (List[RelevanceCourse]): Список курсов с оценкой релевантности.
    """
    RelevanceCourse = create_relevance_course_model(course_names)

    return create_model(
        "RelevanceCourseList",
        courses=(
            List[RelevanceCourse],
            Field(..., description="Список курсов с оценкой релевантности"),
        ),
    )
