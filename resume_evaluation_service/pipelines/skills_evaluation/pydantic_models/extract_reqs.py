"""Модель данных для парсинга текста блока 'Требования' из вакансии."""

from pydantic import BaseModel, Field

class ParsedJobRequirements(BaseModel):
    """
    Схема для возврата текста блока 'Требования' из вакансии.
    
    Attributes:
        requirements_text (str): Полный текст блока требований в оригинальном виде.
    """

    requirements_text: str = Field(
        ..., description="Полный текст блока требований в оригинальном виде."
    )
