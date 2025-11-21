"""
    Функция для создания запроса для парсинга вакансии с структурированным выводом 
    с постепенным изменением температуры
"""

import asyncio
from typing import Optional

from ....utils.create_llm_with_retries import get_structured_llm
from ....utils.logger import setup_logger
from ..prompts.parsing.prompt_builder import (
    parsing_full_prompt,
)
from ..pydantic_models.parsing import (
    ParsedVacancyData,
)

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10


async def parse_llm(text: str) -> Optional[ParsedVacancyData]:
    """
    Создаёт экземпляр LLM, настроенный на структурированный вывод парсинга вакансии по блокам.
    Температура в запросе плавно увеличивается с номером попытки, что повышает вероятность
    корректного парсинга при повторных вызовах в случае ошибок (например, из-за "грязных" символов).

    Args:
        text (str): Текст вакансии или резюме.

    Returns:
        ChatOpenAI: Экземпляр LLM, привязанный к схеме вывода через `.with_structured_output()`.
    """

    # Последняя ошибка
    last_exception = None

    # Для каждой попытки
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(f"Попытка {attempt}/{MAX_ATTEMPTS}")

        try:
            # Получаем LLM с нужной температурой для этой попытки
            structured_llm = get_structured_llm(
                pydantic_model=ParsedVacancyData, attempt_number=attempt
            )

            # Формируем промпт
            prompt_input = {"vacancy_description": text}
            messages = await parsing_full_prompt.ainvoke(prompt_input)

            # Выполняем запрос
            response = await structured_llm.ainvoke(messages)
            logger.info(f"Успешно получено значение после {attempt} попытки")
            return response

        except Exception as e:
            last_exception = e
            logger.warning(f"Ошибка при попытке {attempt}: {str(e)}")

            if attempt == MAX_ATTEMPTS:
                break

    # Все попытки провалились
    logger.error(
        f"Все {MAX_ATTEMPTS} попыток спарсить текст провалились: {str(last_exception)}",
        exc_info=True,
    )
    return None


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
        result1 = await parse_llm(test_text_1)
        print(f"Результат: {result1}\n")

        # Тест с пробелами
        print("Тест 2: Текст только с пробелами")
        result2 = await parse_llm(test_text_2)
        print(f"Результат: {result2}\n")

        # Тест с пустой строкой
        print("Тест 3: Пустая строка")
        result3 = await parse_llm(test_text_3)
        print(f"Результат: {result3}\n")

        # Тест с None
        print("Тест 4: None")
        result4 = await parse_llm(test_text_4)
        print(f"Результат: {result4}\n")

        # Тест с минимальным текстом
        print("Тест 5: Минимальный текст")
        result5 = await parse_llm(test_text_5)
        print(f"Результат: {result5}\n")

        print("=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

    # Запуск асинхронной функции
    asyncio.run(main())
