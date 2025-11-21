"""
Модуль для сравнения зарплат из вакансии и резюме и генерации отчёта.
"""

from decimal import Decimal
from typing import Any, Optional

from ...utils.logger import setup_logger

# Логирование
logger = setup_logger(__name__)


def format_salary_number(amount: Optional[int]) -> str:
    """Форматирует число с пробелами как разделителями."""
    if amount is None:
        return "не указана"
    return f"{amount:,}".replace(",", " ")


def format_salary_range(salary: dict) -> Optional[str]:
    """Форматирует диапазон зарплаты на основе объекта SalaryData."""
    
    # Проверка на None или не указанные данные
    if salary is None or not salary.get('is_specified'):
        return None
    
    min_amount = salary.get('min_amount')
    max_amount = salary.get('max_amount')

    if min_amount is not None and max_amount is not None:
        return f"{format_salary_number(min_amount)} – {format_salary_number(max_amount)} руб./мес."
    elif min_amount is not None:
        return f"от {format_salary_number(min_amount)} руб./мес."
    elif max_amount is not None:
        return f"до {format_salary_number(max_amount)} руб./мес."
    else:
        return None


def compare_salaries(
    resume_salary: dict, vacancy_salary: dict
) -> dict[str, Any]:
    """
    Сравнивает ожидаемую зарплату из резюме с предложением из вакансии.

    Args:
        resume_salary: Объект SalaryData из резюме.
        vacancy_salary: Объект SalaryData из вакансии.

    Returns:
        Словарь с оценкой, сообщением, форматированными данными и отклонением.
    """
    logger.info("Готовим отчет...")
    
    # Если зарплата не указана ни в резюме, ни в вакансии
    if not resume_salary.get('is_specified') and not vacancy_salary.get('is_specified'):
        return {
            "score": 5,
            "message": "Зарплата не указана ни в резюме, ни в вакансии",
            "resume_salary": None,
            "resume_text": None,
            "vacancy_salary": None,
            "vacancy_text": None,
            "deviation_percent": None,
        }
    
    # Если зарплата не указана в резюме
    if not resume_salary.get('is_specified'):
        return {
            "score": 5,
            "message": "Зарплата не указана в резюме",
            "resume_salary": None,
            "resume_text": None,
            "vacancy_salary": format_salary_range(vacancy_salary),
            "vacancy_text": vacancy_salary.get('extracted_text')
            if vacancy_salary.get('is_specified')
            else None,
            "deviation_percent": None,
        }

    # Если зарплата не указана в вакансии
    if not vacancy_salary.get('is_specified'):
        return {
            "score": 5,
            "message": "Зарплата не указана в вакансии",
            "resume_salary": format_salary_range(resume_salary),
            "resume_text": resume_salary.get('extracted_text'),
            "vacancy_salary": None,
            "vacancy_text": None,
            "deviation_percent": None,
        }

    # Определяем суммы для сравнения
    # В резюме: приоритет — min, иначе max
    resume_amount = resume_salary.get('min_amount') or resume_salary.get('max_amount')
    # В вакансии: приоритет — max, иначе min
    vacancy_amount = vacancy_salary.get('max_amount') or vacancy_salary.get('min_amount')

    if resume_amount is None or vacancy_amount is None:
        return {
            "score": 5,
            "message": "Не удалось определить сумму зарплаты",
            "resume_salary": format_salary_range(resume_salary),
            "resume_text": resume_salary.get('extracted_text'),
            "vacancy_salary": format_salary_range(vacancy_salary),
            "vacancy_text": vacancy_salary.get('extracted_text'),
            "deviation_percent": None,
        }

    # Рассчитываем отклонение в процентах
    deviation = (
        (Decimal(str(resume_amount)) - Decimal(str(vacancy_amount)))
        / Decimal(str(vacancy_amount))
    ) * 100
    deviation_rounded = round(float(deviation), 2)

    # Оценка по шкале
    if resume_amount <= vacancy_amount or deviation <= 10:
        score = 5
        message = (
            "Ожидания по ЗП в резюме ниже или незначительно выше предложения (до 10%)"
        )
    elif deviation <= 30:
        score = 4
        message = "Ожидания по ЗП выше предложения на 10–30%"
    elif deviation <= 60:
        score = 3
        message = "Ожидания по ЗП выше предложения на 30–60%"
    elif deviation <= 80:
        score = 2
        message = "Ожидания по ЗП выше предложения на 60–80%"
    elif deviation <= 100:
        score = 1
        message = "Ожидания по ЗП выше предложения на 80–100%"
    else:
        score = 0
        message = "Ожидания по ЗП выше предложения более чем на 100%"

    logger.info("Отчет создан")
    return {
        "score": score,
        "message": message,
        "resume_salary": format_salary_range(resume_salary),
        "resume_text": resume_salary.get('extracted_text'),
        "vacancy_salary": format_salary_range(vacancy_salary),
        "vacancy_text": vacancy_salary.get('extracted_text'),
        "deviation_percent": deviation_rounded,
    }
