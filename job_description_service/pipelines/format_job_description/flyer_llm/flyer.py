"""
Функция для создания запроса для генерации описания вакансии для флаера с структурированным выводом 
с постепенным изменением температуры
"""

import asyncio
from typing import Optional

from utils.create_llm_with_retries import get_structured_llm
from utils.logger import setup_logger
from pipelines.format_job_description.prompts.flyer.prompt_builder import flyer_full_prompt
from pydantic_models.flyer_format import (
    FlyerFormat,
)

# Логирование
logger = setup_logger(__name__)

# Максимальное количество попыток
MAX_ATTEMPTS = 10


async def flyer_llm(text: str) -> Optional[FlyerFormat]:
    """
    Создаёт экземпляр LLM, настроенный на структурированный вывод оптсания вакансии в формате флаера.
    Температура модели плавно увеличивается с номером попытки, что повышает вероятность
    корректного парсинга при повторных вызовах в случае ошибок (например, из-за "грязных" символов).

    Args:
        pydantic_model: Класс Pydantic-модели, которая будет использоваться как схема вывода.
        attempt_number: Номер текущей попытки (от 1 до MAX_ATTEMPTS). Определяет уровень температуры.

    Returns:
        ChatOpenAI: Экземпляр LLM, привязанный к схеме вывода через `.with_structured_output()`.
    """

    # Последняя ошибка
    last_exception = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(f"Попытка {attempt}/{MAX_ATTEMPTS}")

        try:
            # Получаем LLM с нужной температурой для этой попытки
            structured_llm = get_structured_llm(
                pydantic_model=FlyerFormat, attempt_number=attempt
            )

            # Формируем промпт
            prompt_input = {"vacancy": text}
            messages = await flyer_full_prompt.ainvoke(prompt_input)

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
        {"position":"Специалист по обработке документации (бумажный носитель), средний уровень","responsibilities":{"task_1":"Прием и проверка поступающих бухгалтерских и перевозочных документов","task_2":"Отработка и обработка запросов контрагентов","task_3":"Сканирование и архивация документов в соответствии с установленными стандартами","task_4":"Оформление номенклатурных дел и ведение делопроизводства","task_5":"Работа в 1С: ЭДО и Элар для обработки электронных документов"},"requirements":{"requirement_1":"Навыки работы с 1С: ЭДО и Элар, MS Word, Excel, Outlook","requirement_2":"Опыт работы с бухгалтерскими и перевозочными документами будет преимуществом","requirement_3":"Опыт работы в обработке документации не менее 1 года","requirement_4":"Среднее специальное или высшее образование в области делопроизводства или бухгалтерского учета","requirement_5":"Организованность, ответственность, аккуратность и коммуникабельность"}}
        """

        # Тест 2: Текст только с пробелами
        test_text_2 = "   \n\t  "

        # Тест 3: Пустой текст
        test_text_3 = ""

        # Тест 4: None (если возможно)
        test_text_4 = None

        print("=== ТЕСТИРОВАНИЕ ФУНКЦИИ ===\n")

        # Тест с нормальным текстом
        print("Тест 1: Нормальный текст вакансии")
        result1 = await flyer_llm(test_text_1)
        print(f"Результат: {result1}\n")

        # Тест с пробелами
        print("Тест 2: Текст только с пробелами")
        result2 = await flyer_llm(test_text_2)
        print(f"Результат: {result2}\n")

        # Тест с пустой строкой
        print("Тест 3: Пустая строка")
        result3 = await flyer_llm(test_text_3)
        print(f"Результат: {result3}\n")

        # Тест с None
        print("Тест 4: None")
        result4 = await flyer_llm(test_text_4)
        print(f"Результат: {result4}\n")

        print("=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

    # Запуск асинхронной функции
    asyncio.run(main())
