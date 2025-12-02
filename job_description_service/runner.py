"""
Раннер модуля resume_evaluation_service.
Запускает полный пайплайн: извлечение → сравнение → отчёт.
"""

from typing import Any, Dict

from pipelines.format_job_description.runner import get_format_sync
from pipelines.job_description.runner import get_job_description_sync
from utils.logger import setup_logger
from get_report import get_report

# Логирование
logger = setup_logger(__name__)


def run_pipeline(text: str) -> Dict[str, Any]:
    """
    Основная функция пайплайна — принимает текст и возвращает отчёт.
    """
    logger.info("Запуск модуля: job_description_service")

    # === Шаг 1: Генерация описания вакансии ===
    logger.info("Генерация описания вакансии запущена")
    try:
        job_description = get_job_description_sync(input=text)
        
        # Проверка статуса structured_job_description
        if job_description is None or job_description.get("status") == "failed":
            logger.error("Ошибка: Не удалось извлечь генерацию описания вакансии для работного сайта")
            return {
                "message": "Ошибка: Не удалось извлечь генерацию описания вакансии для работного сайта",
                "job_description": None, 
                "job_formats": None,
                "status": "failed"
            }
        
        logger.info("Генерация описания вакансии успешно завершена")
    except Exception as e:
        logger.error(
            f"Ошибка при генерации описания вакансии: {str(e)}", exc_info=True
        )
        return {
            "message": "Ошибка: Не удалось извлечь генерацию описания вакансии для работного сайта",
            "job_description": None, 
            "job_formats": None,
            "status": "failed"
        }

    # Преобразуем в строку тк так во всех функциях настроено все на текст
    job_description_data = f"{job_description}" # todo
    
    # === Шаг 2: Генерация описаний для различных форматов ===
    logger.info("Генерация описания для различных форматов")
    try:
        job_formats = get_format_sync(input=job_description_data)
        
        # Проверка статуса structured_job_description
        if job_formats is None or job_formats.get("status") == "failed":
            logger.error("Ошибка: Не удалось извлечь генерацию описания вакансии для других ресурсов")
            return {
                "message": "Ошибка: Не удалось извлечь генерацию описания вакансии для других ресурсов",
                "job_description": job_description, 
                "job_formats": None,
                "status": "failed"
            }
            
            
        logger.info("Генерация описания для различных форматов успешно завершена")
    except Exception as e:
        logger.error(f"Ошибка при генерации : {str(e)}", exc_info=True)
        return {
            "message": "Ошибка: Не удалось извлечь генерацию описания вакансии для других ресурсов",
            "job_description": job_description, 
            "job_formats": None,
            "status": "failed"
        }

    # === Шаг 3: Формируем общий отчёт ===
    report_raw = {"job_description": job_description, "job_formats": job_formats}

    final_report = get_report(report_raw)

    logger.info("Полный пайплайн генерации описания вакансии завершён")
    return final_report


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

    report = run_pipeline(text=vacancy_text)
    print(report)


if __name__ == "__main__":
    main()
