"""
Раннер модуля resume_evaluation_service.
Запускает полный пайплайн: извлечение → сравнение → отчёт.
"""
import asyncio
from typing import Any, Dict

from .pipelines.additional_evaluation.runner import evaluate_additional_match
from .pipelines.education_evaluation.runner import evaluate_education_match_pipeline
from .pipelines.salary_evaluation.runner import evaluate_salary_match
from .pipelines.work_exp_evaluation.runner import evaluate_work_experience_pipeline
from .pipelines.skills_evaluation.runner import evaluate_skills_pipeline
from .utils.logger import setup_logger

# Логирование
logger = setup_logger(__name__)


async def run_pipeline(vacancy_text: str, resume_text: str) -> Dict[str, Any]:
    """
    Основная функция пайплайна — принимает тексты и возвращает отчёт.
    Может быть вызвана извне (например, из worker.py).
    """
    logger.info("Запуск модуля: resume_evaluation_service")

    try:
        # Запускаем параллельно все блоки оценки
        # === 1: Оценка зарплаты ===
        salary_report_task = evaluate_salary_match(
            resume_text=resume_text, vacancy_text=vacancy_text
        )

        # === 2: Оценка образования и курсов ===
        education_report_task = evaluate_education_match_pipeline(
            resume_text=resume_text, vacancy_text=vacancy_text
        )

        # === 3: Оценка условий работы ===
        additional_report_task = evaluate_additional_match(
            resume_text=resume_text, vacancy_text=vacancy_text
        )

        # === 4: Оценка условий работы ===
        work_experience_report_task = evaluate_work_experience_pipeline(
                resume_text=resume_text, vacancy_text=vacancy_text
            )

        # === 5: Оценка скиллов ===
        skills_report_task = evaluate_skills_pipeline(
            resume_text=resume_text, vacancy_text=vacancy_text
        )

        # Параллельное выполнение задач
        parsing_results = await asyncio.gather(
            salary_report_task,
            education_report_task,
            additional_report_task,
            work_experience_report_task,
            skills_report_task,
            return_exceptions=True,
        )

        salary_report_data, education_report_data, additional_report_data, work_experience_report_data, skills_report_data = parsing_results

    except Exception as e:
        logger.error(
            f"Ошибка при извлечении данных в одном из блоков: {str(e)}", exc_info=True
        )
        return {"status": "failed"}

    # Проверка на наличие отчета по зарплатным ожиданиям
    if salary_report_data is None or salary_report_data.get("status") == "failed":
        logger.error("Не удалось получить отчет по зарплатным ожиданиям")
        return {"status": "failed"}

    # Проверка на наличие отчета по образованию
    if education_report_data is None or education_report_data.get("status") == "failed":
        logger.error("Не удалось получить отчет по образованию")
        return {"status": "failed"}

    # Проверка на наличие отчета по дополнительным условиям
    if additional_report_data is None or additional_report_data.get("status") == "failed":
        logger.error("Не удалось получить отчет по условиям работы")
        return {"status": "failed"}

    # Проверка на наличие отчета по опыту работы
    if work_experience_report_data is None or work_experience_report_data.get("status") == "failed":
        logger.error("Не удалось получить отчет по опыту работы")
        return {"status": "failed"}

    # Проверка на наличие отчета по навыкам
    if skills_report_data is None or skills_report_data.get("status") == "failed":
        logger.error("Не удалось получить отчет по навыкам")
        return {"status": "failed"}

    # === Шаг 6: Формируем общий отчёт ===
    final_report = {
        "salary_evaluation": salary_report_data if salary_report_data else None,
        "education_evaluation": education_report_data if education_report_data else None,
        "additional_evaluation": additional_report_data if additional_report_data else None,
        "work_experience_report": work_experience_report_data if work_experience_report_data else None,
        "skills_report": skills_report_data if skills_report_data else None
    }

    print(final_report)
    logger.info("Полный пайплайн завершён")
    return final_report


def run_pipeline_sync(
    vacancy_text: str, resume_text: str,
) -> Dict[str, Any]:
    """Синхронная обёртка."""
    return asyncio.run(run_pipeline(vacancy_text, resume_text))



def main():
    """
    Точка входа при запуске модуля напрямую.
    Использует тестовые данные.
    """
    # Тестовые данные — только для запуска вручную
    vacancy_text = """
    Вакансия: Python-разработчик в IT-компанию.
    Зарплата: от 120 000 до 150 000 рублей.
    Условия: работа в офисе и удалённо, премии, ДМС.
    Требования: опыт от 3 лет, знание Django, FastAPI.
    Образование: высшее в области информатики или смежных дисциплин.
    Условия: 5/2 с 10 до 18, полный день
    """

    resume_text = """
    Иван Иванов, backend-разработчик.
    Опыт: 4 года.
    Ожидаемая зарплата: 140 000 рублей.
    Навыки: Python, Flask, Docker, PostgreSQL, Git.
    Образование: высшее, специальность — программная инженерия.
    Курсы: Python для анализа данных, Основы машинного обучения.
    График: Полный день, 5/2
    """

    report = run_pipeline_sync(vacancy_text, resume_text)
    print(report)


if __name__ == "__main__":
    main()
