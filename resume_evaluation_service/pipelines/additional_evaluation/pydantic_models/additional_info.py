"""Модель для дополнительной информации"""

from pydantic import BaseModel, Field
from typing import List, Literal

# Допустимые категории графика работы
work_schedule_types = [
    "Полный день",
    "Неполный день",
    "Гибкий график",
    "Сменный график",
    "Удалённая работа",
    "Частичная занятость",
    "Полная занятость",
    "Вахтовый метод",
    "Другое"
]

ScheduleLiteral = Literal[tuple(work_schedule_types)]

class WorkScheduleInfo(BaseModel):
    """
    Информация о графике работы
    
    Attributes:
        schedule: Тип графика работы
        details: Дополнительные детали (например, 'с 9 до 18', 'удалённо с возможностью командировок')
    """
    schedule: List[ScheduleLiteral] = Field(..., description="Тип графика работы")
    details: str = Field("", description="Дополнительные детали (например, 'с 9 до 18', 'удалённо с возможностью командировок')")

class WorkScheduleComparison(BaseModel):
    """
    Результат сравнения графиков работы из вакансии и резюме
    """
    vacancy_schedule: WorkScheduleInfo = Field(..., description="График из вакансии")
    resume_schedule: WorkScheduleInfo = Field(..., description="Желаемый график кандидата из резюме")
    match: bool = Field(..., description="Соответствует ли график кандидата требованиям вакансии")
    reason: str = Field(..., description="Обоснование соответствия")
