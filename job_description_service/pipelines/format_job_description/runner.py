"""
Финальный runner: структурирует входные данные → генерирует вакансию в разных форматах → возвращает отчёт.
"""

import asyncio
from typing import Any, Dict

from utils.logger import setup_logger
from pipelines.format_job_description.get_flyer_format import get_flyer_format
from pipelines.format_job_description.get_media_format import get_media_format
from pipelines.format_job_description.get_social_media_format import get_social_media_format

# Логирование
logger = setup_logger(__name__)


async def get_format(input: str) -> Dict[str, Any]:
    """
    Полный пайплайн: извлечение + генерация форматов описания + отчёт.
    """

    # Проверка на пустой или почти пустой input
    if not input or not input.strip():
        logger.error("Ошибка: Входные данные пусты или содержат только пробелы")
        return {
            "message": "Ошибка: Входные данные пусты или содержат только пробелы",
            "structured_job_description": None,
            "status": "failed"
        }

    # Парсим структурированные входные данные
    logger.info("Начинаем генерировать вакансию в различных форматах")

    # Параллельное выполнение задач для форматирования вакансии в разных форматах
    flyer_task = get_flyer_format(input)
    media_task = get_media_format(input)
    social_media_task = get_social_media_format(input)

    try:
        flyer_data, media_data, social_media_data = await asyncio.gather(
            flyer_task, media_task, social_media_task
        )
    except Exception as e:
        logger.error(f"Ошибка при извлечении структурированных данных: {str(e)}")
        return {
            "message": f"Ошибка при извлечении структурированных данных: {str(e)}",
            "structured_job_description": None,
            "status": "failed"
        }

    # Проверка, что не None
    if flyer_data is None:
        logger.error("Ошибка: Не удалось извлечь данные для флаера из входного текста")
        return {
            "message": "Ошибка: Не удалось извлечь данные для флаера из входного текста",
            "structured_job_description": None,
            "status": "failed"
        }

    if media_data is None:
        logger.error("Ошибка: Не удалось извлечь данные для тв/газеты из входного текста")
        return {
            "message": "Ошибка: Не удалось извлечь данные для тв/газеты из входного текста",
            "structured_job_description": None,
            "status": "failed"
        }

    if social_media_data is None:
        logger.error("Ошибка: Не удалось извлечь данные для соц. сетей из входного текста")
        return {
            "message": "Ошибка: Не удалось извлечь данные для соц. сетей из входного текста",
            "structured_job_description": None,
            "status": "failed"
        }
         
    
    logger.info("Генерация вакансии в различных форматах успешно выполнена")
    return {
        "message": "Успешно",
        "flyer_data": flyer_data,
        "media_data": media_data,
        "social_media_data": social_media_data,
        "status": "success"
    }


def get_format_sync(input: str) -> Dict[str, Any]:
    """Синхронная обёртка."""
    return asyncio.run(get_format(input))


# Тестовые данные
if __name__ == "__main__":

    async def main():
        # Тест 1: Нормальный текст вакансии
        test_text_1 = """
        {"position":"Специалист по обработке документации (бумажный носитель), средний уровень","responsibilities":{"task_1":"Прием и проверка поступающих бухгалтерских и перевозочных документов","task_2":"Отработка и обработка запросов контрагентов","task_3":"Сканирование и архивация документов в соответствии с установленными стандартами","task_4":"Оформление номенклатурных дел и ведение делопроизводства","task_5":"Работа в 1С: ЭДО и Элар для обработки электронных документов"},"requirements":{"requirement_1":"Навыки работы с 1С: ЭДО и Элар, MS Word, Excel, Outlook","requirement_2":"Опыт работы с бухгалтерскими и перевозочными документами будет преимуществом","requirement_3":"Опыт работы в обработке документации не менее 1 года","requirement_4":"Среднее специальное или высшее образование в области делопроизводства или бухгалтерского учета","requirement_5":"Организованность, ответственность, аккуратность и коммуникабельность"}}
        """

        # Тест 2: Текст только с пробелами
        test_text_2 = "   \n\t  "

        # Тест 3: Пустой текст
        test_text_3 = ""

        # Тест 4: None (если возможно)
        test_text_4 = None

        print("=== ТЕСТИРОВАНИЕ ФУНКЦИИ parse_llm ===\n")

        # Тест с нормальным текстом
        print("Тест 1: Нормальный текст вакансии")
        result1 = await get_format(test_text_1)
        print(f"Результат: {result1}\n")

        # Тест с пробелами
        print("Тест 2: Текст только с пробелами")
        result2 = await get_format(test_text_2)
        print(f"Результат: {result2}\n")

        # Тест с пустой строкой
        print("Тест 3: Пустая строка")
        result3 = await get_format(test_text_3)
        print(f"Результат: {result3}\n")

        # Тест с None
        print("Тест 4: None")
        result4 = await get_format(test_text_4)
        print(f"Результат: {result4}\n")

        print("=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

    # Запуск асинхронной функции
    asyncio.run(main())
