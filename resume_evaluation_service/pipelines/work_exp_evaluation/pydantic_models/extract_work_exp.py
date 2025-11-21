"""Модель данных извлечения опыта работы из резюме"""

from typing import List, Optional

from pydantic import BaseModel, Field


class WorkExpInfo(BaseModel):
    """
    Модель данных единичного опыта работы
    
    Attributes:
        company_name (str): Название компании
        position (str): Название должности в этой компании, где работал кандидат
        work_tasks (str): Задачи и обязанности, которые кандидат выполнял на рабочем месте, если указано. Также достижения на работе
        start_date (Optional[date]): Дата начала работы, если указано
        end_date (Optional[date]): Дата окончания работы, если указано
        duration (str): Продолжительность работы в формате "годы-месяцы"
        currently_working (bool): Флаг, указывающий, работает ли кандидат в этой компании в настоящее время
    """
    company_name: str = Field(..., description="Название компании")
    position: str = Field(
        ..., description="Название должности в этой компании, где работал кандидат"
    )
    work_tasks: str = Field(
        None,
        description="Задачи и обязанности, которые кандидат выполнял на рабочем месте, если указано. Также достижения на работе",
    )
    start_date: Optional[str] = Field(
        None, description="Дата начала работы, если указано"
    )
    end_date: Optional[str] = Field(
        None, description="Дата окончания работы, если указано"
    )
    duration: Optional[str] = Field(
        None,
        description="Длительность работы на данной должности, если указано в резюме",
    )
    currently_working: bool = Field(
        False, description="Работает ли сейчас в этой компании"
    )


class WorkExpList(BaseModel):
    """
    Список информации 'опытов работы'
    
    Attributes:
        work_list (List[WorkExpInfo]): Список информации о работе
        full_work_exp_years (int): Количество полных лет опыта кандидата в общем стаже (если указано)
        work_exp_month_after_year (int): Количество остатка месяцев после полных лет опыта (если указано)
    """
    work_list: List[WorkExpInfo]
    full_work_exp_years: int = Field(
        None,
        description="Количество полных лет опыта кандидата в общем стаже (если указано)",
    )
    work_exp_month_after_year: int = Field(
        None,
        description="Количество остатка месяцев после полных лет опыта (если указано)",
    )
