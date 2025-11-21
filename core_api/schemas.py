"""
Схемы данных для валидации запросов и ответов API

Модуль определяет Pydantic модели для:
1. SalaryComparisonRequest - запрос на сравнение резюме и вакансии
2. JobDescriptionRequest - запрос на генерацию описания вакансии
3. SalaryComparisonResult - результат сравнения резюме и вакансии

Все модели используют валидацию Pydantic для обеспечения
корректности входных и выходных данных.
"""

from typing import Optional
from pydantic import BaseModel

class SalaryComparisonRequest(BaseModel):
    vacancy_text: Optional[str] = None
    resume_text: Optional[str] = None

class JobDescriptionRequest(BaseModel):
    input_data: Optional[str] = None

class SalaryComparisonResult(BaseModel):
    status: str
    data: dict
