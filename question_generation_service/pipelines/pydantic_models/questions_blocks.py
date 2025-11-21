"""Модели данных для блоков вопросов"""

from typing import Optional

from pydantic import BaseModel, Field


class Question(BaseModel):
    """
    Базовая модель вопроса
    
    Attributes:
        question (str): Текст вопроса
        details (Optional[str]): Описание почему был задан этот вопрос
    """
    question: str = Field(..., description="Текст вопроса")
    details: Optional[str] = Field(
        None, description="Описание почему был задан этот вопрос"
    )
    

class StandardQuestionBlock(BaseModel):
    """
    Модель подблока вопросов
    
    Attributes:
        q_1 (Question): Первый вопрос в блоке
        q_2 (Question): Второй вопрос в блоке
    """
    q_1: Question
    q_2: Question
    

class ExperienceBlock(BaseModel):
    """
    Модель блока про опыт работы
    """
    professional_skills: StandardQuestionBlock = Field(
        ..., description="Вопросы о профессиональных навыках"
    )
    practical_examples: StandardQuestionBlock = Field(
        ..., description="Вопросы о практических примерах"
    )
    past_situations: StandardQuestionBlock = Field(
        ..., description="Вопросы о прошлых ситуациях"
    )
    career_goals: StandardQuestionBlock = Field(
        ..., description="Вопросы о карьерных целях"
    )


class MotivationBlock(BaseModel):
    """
    Модель блока мотивации
    
    Attributes:
        career_ambitions (StandardQuestionBlock): Вопросы о карьерных амбициях
        job_search_factors (StandardQuestionBlock): Вопросы о факторах поиска работы
        salary_expectations (StandardQuestionBlock): Вопросы о зарплатных ожиданиях
        company_role (StandardQuestionBlock): Вопросы о роли в компании
        motivation_goals (StandardQuestionBlock): Вопросы о целях и мотивации
    """
    career_ambitions: StandardQuestionBlock = Field(
        ..., description="Вопросы о карьерных амбициях"
    )
    job_search_factors: StandardQuestionBlock = Field(
        ..., description="Вопросы о факторах поиска работы"
    )
    salary_expectations: StandardQuestionBlock = Field(
        ..., description="Вопросы о зарплатных ожиданиях"
    )
    company_role: StandardQuestionBlock = Field(
        ..., description="Вопросы о роли в компании"
    )
    motivation_goals: StandardQuestionBlock = Field(
        ..., description="Вопросы о целях и мотивации"
    )


class PersonalBlock(BaseModel):
    """
    Модель личностного блока
    
    Attributes:
        past_qualities (StandardQuestionBlock): Вопросы о проявленных качествах
        soft_skills (StandardQuestionBlock): Вопросы о софт-скиллах
        development_vision (StandardQuestionBlock): Вопросы о видении развития
    """
    past_qualities: StandardQuestionBlock = Field(
        ..., description="Вопросы о проявленных качествах"
    )
    soft_skills: StandardQuestionBlock = Field(
        ..., description="Вопросы о софт-скиллах"
    )
    development_vision: StandardQuestionBlock = Field(
        ..., description="Вопросы о видении развития"
    )