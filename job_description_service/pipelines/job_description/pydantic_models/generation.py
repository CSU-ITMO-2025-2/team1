"""Модель данных для генерации описания вакансии"""

from typing import Optional

from pydantic import BaseModel, Field


class TaskSection(BaseModel):
    """
    Модель данных для описания основных задач в вакансии.
    
    
    Attributes:
        task_1 (Optional[str]): Первая задача
        task_2 (Optional[str]): Вторая задача
        task_3 (Optional[str]): Третья задача
        task_4 (Optional[str]): Четвертая задача
        task_5 (Optional[str]): Пятая задача
    """

    task_1: Optional[str] = Field(None, description="Первая задача")
    task_2: Optional[str] = Field(None, description="Вторая задача")
    task_3: Optional[str] = Field(None, description="Третья задача")
    task_4: Optional[str] = Field(None, description="Четвертая задача")
    task_5: Optional[str] = Field(None, description="Пятая задача")


class RequirementSection(BaseModel):
    """
    Модель данных для описания требований к кандидату.

    Attributes:
        requirement_1: Первое требование
        requirement_2: Второе требование
        requirement_3: Третье требование
        requirement_4: Четвертое требование
        requirement_5: Пятое требование
    """

    requirement_1: Optional[str] = Field(None, description="Первое требование")
    requirement_2: Optional[str] = Field(None, description="Второе требование")
    requirement_3: Optional[str] = Field(None, description="Третье требование")
    requirement_4: Optional[str] = Field(None, description="Четвертое требование")
    requirement_5: Optional[str] = Field(None, description="Пятое требование")


class GeneratedVacancyDescription(BaseModel):
    """
    Модель сгенерированного описания вакансии.

    Attributes:
        position: Название должности
        responsibilities: Основные задачи и обязанности
        requirements: Требования к кандидату
    """

    position: str = Field(
        ...,
        description="Название должности",
    )

    responsibilities: TaskSection = Field(
        ...,
        description="Основные задачи и обязанности",
    )

    requirements: RequirementSection = Field(
        ...,
        description="Требования к кандидату",
    )
