"""Модель описания вакансии для флаера"""

from pydantic import BaseModel, Field

class FlyerFormat(BaseModel):
    """
    Модель описания вакансии для флаера
    
    Attributes:
        company_info: Краткая информация о компании и сфере деятельности (1 предложение)
        job_details: Описание проекта и обязанностей (2-3 предложения)
        requirements: Критичные требования (2 предложения)
    """

    company_info: str = Field(
        ...,
        description="Краткая информация о компании и сфере деятельности (1 предложение)",
    )
    job_details: str = Field(
        ..., description="Описание проекта и обязанностей (2-3 предложения)"
    )
    requirements: str = Field(..., description="Критичные требования (2 предложения)")
