"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс парсинга вакансии.
"""

import asyncio
from typing import Optional

from ...utils.clean_text import clean_text
from ...utils.logger import setup_logger
from .parsing_llm.parsing import parse_llm
from .pydantic_models.parsing import ParsedVacancyData

# Логирование
logger = setup_logger(__name__)


async def get_structured_input(text: str) -> Optional[ParsedVacancyData]:
    """
    Асинхронно извлекает и структурирует данные из входного текста.

    Args:
        text (str): Текст входных данных.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем, что входной текст присутствует и не пустой
    if not text or not text.strip():
        logger.warning("Пустой текст для парсинга вакансии")
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_text = clean_text(text)

    try:
        # Вызываем функцию для парсинга вакансии
        result = await parse_llm(cleaned_text)
        
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
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
        result1 = await get_structured_input(test_text_1)
        print(f"Результат: {result1}\n")

        # Тест с пробелами
        print("Тест 2: Текст только с пробелами")
        result2 = await get_structured_input(test_text_2)
        print(f"Результат: {result2}\n")

        # Тест с пустой строкой
        print("Тест 3: Пустая строка")
        result3 = await get_structured_input(test_text_3)
        print(f"Результат: {result3}\n")

        # Тест с None
        print("Тест 4: None")
        result4 = await get_structured_input(test_text_4)
        print(f"Результат: {result4}\n")

        # Тест с минимальным текстом
        print("Тест 5: Минимальный текст")
        result5 = await get_structured_input(test_text_5)
        print(f"Результат: {result5}\n")

        print("=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

    # Запуск асинхронной функции
    asyncio.run(main())
