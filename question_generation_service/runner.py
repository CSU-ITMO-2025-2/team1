"""
Раннер модуля question_generation_service.
Запускает полный пайплайн: извлечение → сравнение → отчёт.
"""
import asyncio
from typing import Any, Dict

from pipelines.generate_experience_block import get_experience_block
from pipelines.generate_motivation_block import get_motivation_block
from pipelines.generate_personal_block import get_personal_block
from utils.logger import setup_logger
from utils.prepare_work_evaluation_report import format_work_experience_report
from utils.prepare_skills_evaluation_report import format_skills_report
from utils.prepare_salary_evaluation_report import format_salary_report


# Логирование
logger = setup_logger(__name__)


async def run_pipeline(vacancy: str, resume: str, report: dict) -> dict:
    """
    Основная функция пайплайна — принимает текст и возвращает отчёт.
    """
    logger.info("Запуск модуля: question_generation_service")

    # Проверка на пустой или почти пустой input
    if not vacancy or not vacancy.strip():
        logger.error("Ошибка: Входные данные пусты или содержат только пробелы")
        return {
            "message": "Ошибка: Входные данные пусты или содержат только пробелы",
            "status": "failed"
        }

    if not resume or not resume.strip():
        logger.error("Ошибка: Входные данные пусты или содержат только пробелы")
        return {
            "message": "Ошибка: Входные данные пусты или содержат только пробелы",
            "status": "failed"
        }

    if not report:
        logger.error("Ошибка: Входные данные пусты или содержат только пробелы")
        return {
            "message": "Ошибка: Входные данные пусты или содержат только пробелы",
            "status": "failed"
        }


    # Подготовим данные по оценке резюме

    work_exp_report_block = format_work_experience_report(report)
    skills_report_block = format_skills_report(report)
    salary_report_block = format_salary_report(report)
    print(work_exp_report_block)
    print(skills_report_block)
    print(salary_report_block)


    # Распаралеливаем задачи на парсинг и генерацию софт скиллов
    experience_block_task = get_experience_block(vacancy, resume, work_exp_report_block, skills_report_block)
    motivation_block_task = get_motivation_block(vacancy, resume, work_exp_report_block, salary_report_block)
    personal_block_task = get_personal_block(vacancy, resume, work_exp_report_block)

    try:
        experience_block_data, motivation_block_data, personal_block_data = await asyncio.gather(
            experience_block_task, motivation_block_task, personal_block_task,
            return_exceptions=True,
        )
    except Exception as e:
        logger.error(f"Ошибка при извлечении структурированных данных: {str(e)}")
        return {
            "status": "failed"
        }

    if experience_block_data is None or experience_block_data.get("status") == "failed":
        return {
            "status": "failed"
        }

    if motivation_block_data is None or motivation_block_data.get("status") == "failed":
        return {
            "status": "failed"
        }

    if personal_block_data is None or personal_block_data.get("status") == "failed":
        return {
            "status": "failed"
        }

        # === Шаг 3: Формируем общий отчёт ===
    report = {
        "experience": experience_block_data,
        "motivation": motivation_block_data,
        "personal": personal_block_data
    }

    logger.info("Полный пайплайн генерации описания вакансии завершён")
    return report

def run_pipeline_sync(
    vacancy: str, resume: str, report: dict
) -> Dict[str, Any]:
    """Синхронная обёртка для пайплайна оценки навыков."""
    return asyncio.run(run_pipeline(vacancy=vacancy, resume=resume, report=report))


async def main():
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
    Обязанности: разработка backend-сервисов, написание API, работа с базами данных.
    Условия: 5/2 с 10 до 18, полный день.
    Мы ищем опытного разработчика в дружную команду.
    """

    resume_text = """
    Иван Иванов, backend-разработчик.
    Опыт: 4 года работы с Python.
    Текущая должность: Middle Python Developer в компании TechCorp.
    Ожидаемая зарплата: 140 000 рублей.
    Навыки: Python, Flask, Docker, PostgreSQL, Git, REST API.
    Образование: высшее, специальность — программная инженерия.
    Курсы: Python для анализа данных, Основы машинного обучения.
    График: Полный день, 5/2.
    О себе: ответственный, умею работать в команде, готов к изучению новых технологий.
    Причина поиска: хочу профессионального роста и интересных задач.
    """

    # Пустой словарь для отчета (как требуется в функции)
    report_dict = {'score': 'good'}

    # Запускаем пайплайн напрямую, так как мы уже в асинхронном контексте
    report = await run_pipeline(
        vacancy=vacancy_text,
        resume=resume_text,
        report=report_dict
    )

    # Выводим результат в формате JSON для удобства чтения
    import json
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
