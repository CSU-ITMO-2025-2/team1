"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс генерации описания вакансии для медиа ресурсов.
"""

import asyncio
from typing import Optional

from ...utils.clean_text import clean_text
from ...utils.logger import setup_logger
from .media_llm.media import media_llm
from .pydantic_models.media import MediaFormat

# Логирование
logger = setup_logger(__name__)

async def get_media_format(text: str) -> Optional[MediaFormat]:
    """
    Асинхронно генерирует вакансию в формате тв/газеты из входного текста.

    Args:
        text (str): Текст входных данных.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем что текст не пустой и не состоит только из пробелов
    if not text or not text.strip():
        logger.warning("Пустой текст для парсинга")
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_text = clean_text(text)

    try:
        # Запускаем генерацию описания вакансии в формате тв/газеты
        result = await media_llm(cleaned_text)
        
        # Проверяем, что результат не None
        if result is None:
            logger.warning("Результат равен None")
            return {'status': 'failed'}
        
        # Переводим в словарь
        result_dict = result.model_dump()
        
        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}


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
        result1 = await get_media_format(test_text_1)
        print(f"Результат: {result1}\n")

        # Тест с пробелами
        print("Тест 2: Текст только с пробелами")
        result2 = await get_media_format(test_text_2)
        print(f"Результат: {result2}\n")

        # Тест с пустой строкой
        print("Тест 3: Пустая строка")
        result3 = await get_media_format(test_text_3)
        print(f"Результат: {result3}\n")

        # Тест с None
        print("Тест 4: None")
        result4 = await get_media_format(test_text_4)
        print(f"Результат: {result4}\n")

        print("=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

    # Запуск асинхронной функции
    asyncio.run(main())
