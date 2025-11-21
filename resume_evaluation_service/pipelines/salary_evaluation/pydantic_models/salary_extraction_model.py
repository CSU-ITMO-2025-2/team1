"""Модель данных парсинга зарплаты"""

from typing import Optional

from pydantic import BaseModel, Field


class SalaryData(BaseModel):
    """
    Базовая модель для данных о зарплате.
    
    Attributes:
        min_amount: Минимальная указанная зарплата
        max_amount: Максимальная указанная зарплата
        is_specified: Указана ли зарплата явно
        extracted_text: Извлеченный фрагмент текста о зарплате
    """

    min_amount: Optional[int] = Field(
        None, description="Минимальная указанная зарплата"
    )
    max_amount: Optional[int] = Field(
        None, description="Максимальная указанная зарплата"
    )
    is_specified: bool = Field(False, description="Указана ли зарплата явно")
    extracted_text: str = Field(
        "", description="Извлеченный фрагмент текста о зарплате"
    )
