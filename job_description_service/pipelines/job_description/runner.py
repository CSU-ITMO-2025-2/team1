"""
Финальный runner: структурирует входные данные → генерирует описание вакансии для работного сайта → возвращает отчёт.
"""

import asyncio
from typing import Any, Dict

from ...utils.logger import setup_logger
from .generate_job_description import get_structured_job_description
from .generate_soft_skills import get_soft_skills
from .parse_input import get_structured_input

# Логирование
logger = setup_logger(__name__)


async def get_job_description(input: str) -> Dict[str, Any]:
    """
    Полный пайплайн генерации описания вакансии для работного сайта: извлечение + генерация + отчёт.
    """

    logger.info("Парсим структурированные входные данные")

    # Проверка на пустой или почти пустой input
    if not input or not input.strip():
        logger.error("Ошибка: Входные данные пусты или содержат только пробелы")
        return {
            "message": "Ошибка: Входные данные пусты или содержат только пробелы",
            "structured_job_description": None,
            "status": "failed"
        }

    # Распаралеливаем задачи на парсинг и генерацию софт скиллов
    structured_data_parsing_task = get_structured_input(input)
    soft_skills_task = get_soft_skills(input)

    try:
        structured_data, soft_skills_data = await asyncio.gather(
            structured_data_parsing_task, soft_skills_task
        )
    except Exception as e:
        logger.error(f"Ошибка при извлечении структурированных данных: {str(e)}")
        return {
            "message": f"Ошибка при извлечении структурированных данных: {str(e)}",
            "structured_job_description": None,
            "status": "failed"
        }

    # Проверка статуса structured_data
    if structured_data is None or structured_data.get("status") == "failed":
        logger.error("Ошибка: Не удалось извлечь структурированные данные из входного текста")
        return {
            "message": "Ошибка: Не удалось извлечь структурированные данные из входного текста",
            "structured_job_description": None,
            "status": "failed"
        }
    
    # Проверка статуса soft_skills_data
    if soft_skills_data is None or soft_skills_data.get("status") == "failed":
        logger.error("Ошибка: Не удалось извлечь soft skills из входного текста")
        return {
            "message": "Ошибка: Не удалось извлечь soft skills из входного текста",
            "structured_job_description": None,
            "status": "failed"
        }

    try:
        conditions = structured_data.get('conditions')
        education = structured_data.get('education')
        experience = structured_data.get('experience')
        key_skills = structured_data.get('key_skills')
        other = structured_data.get('other')
        position = structured_data.get('position')
        soft_skills = soft_skills_data.get('soft_skills')
        
    except AttributeError as e:
        logger.error(f"Ошибка при доступе к атрибутам структурированных данных: {str(e)}")
        return {
            "message": f"Ошибка при доступе к атрибутам структурированных данных: {str(e)}",
            "structured_job_description": None,
            "status": "failed"
        }

    try:
        # Запускаем генерацию описания вакансии
        structured_job_description = await get_structured_job_description(
            conditions=conditions,
            education=education,
            experience=experience,
            key_skills=key_skills,
            other=other,
            position=position,
            soft_skills=soft_skills,
        )
        
        # Проверка статуса structured_job_description
        if structured_job_description is None or structured_job_description.get("status") == "failed":
            logger.error("Ошибка: Не удалось извлечь генерацию описания вакансии")
            return {
                "message": "Ошибка: Не удалось извлечь soft skills из входного текста",
                "structured_job_description": None,
                "status": "failed"
            }
        
    except Exception as e:
        logger.error(f"Ошибка при генерации описания вакансии: {str(e)}")
        return {
            "message": f"Ошибка при генерации описания вакансии: {str(e)}",
            "structured_job_description": None,
            "status": "failed"
        }
        
    logger.info("Генерация описания вакансии для работного сайта успешно завершена")
    return {
        "message": "Успешно",
        "structured_job_description": structured_job_description,
        "status": "success"
    }


def get_job_description_sync(input: str) -> Dict[str, Any]:
    """Синхронная обёртка."""
    return asyncio.run(get_job_description(input))


# Тестовые данные
if __name__ == "__main__":

    async def main():
        # Тест 1: Нормальный текст вакансии
        test_text_1 = """
        Компания: ТехноСофт
        Вакансия: Senior Python Developer
        Зарплата: от 150 000 до 200 000 рублей
        Требования: Опыт работы с Python от 3 лет, знание FastAPI, Docker
        Условия: Удаленная работа, медицинская страховка, 28 дней отпуска
        Контакт: hr@techsoft.ru
        """

        # Тест 2: Текст только с пробелами
        test_text_2 = "   \n\t  "

        # Тест 3: Пустой текст
        test_text_3 = ""

        # Тест 4: None (если возможно)
        test_text_4 = None

        # Тест 5: Минимальный текст
        test_text_5 = "Python developer, 100000-150000 руб."

        print("=== ТЕСТИРОВАНИЕ ФУНКЦИИ parse_llm ===\n")

        # Тест с нормальным текстом
        print("Тест 1: Нормальный текст вакансии")
        result1 = await get_job_description(test_text_1)
        print(f"Результат: {result1}\n")

        # Тест с пробелами
        print("Тест 2: Текст только с пробелами")
        result2 = await get_job_description(test_text_2)
        print(f"Результат: {result2}\n")

        # Тест с пустой строкой
        print("Тест 3: Пустая строка")
        result3 = await get_job_description(test_text_3)
        print(f"Результат: {result3}\n")

        # Тест с None
        print("Тест 4: None")
        result4 = await get_job_description(test_text_4)
        print(f"Результат: {result4}\n")

        # Тест с минимальным текстом
        print("Тест 5: Минимальный текст")
        result5 = await get_job_description(test_text_5)
        print(f"Результат: {result5}\n")

        print("=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

    # Запуск асинхронной функции
    asyncio.run(main())
