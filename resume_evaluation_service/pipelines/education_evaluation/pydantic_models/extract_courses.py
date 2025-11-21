"""Модель данных для извлечения курсов из резюме"""

from typing import List

from pydantic import BaseModel, Field


class CourseInfo(BaseModel):
    """
    Курс из резюме
    
    Attributes:
        course_name (str): Название курса
        description (str): Краткое описание курса
    """

    course_name: str = Field(..., description="Название курса")
    description: str = Field(..., description="Краткое описание курса")


class CourseList(BaseModel):
    """
    Список курсов из резюме
    
    Attributes:
        course_list (List[CourseInfo]): Список курсов
    """

    course_list: List[CourseInfo]
