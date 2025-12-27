"""
Функция для создания LLM с structured_output и температурой, зависящей от номера попытки.
"""
from langchain_mistralai import ChatMistralAI
import os
from typing import Type

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

# Конфигурация
MAX_ATTEMPTS = 10  # всего 10 попыток на исправление
FINAL_TEMPERATURE = 0.7  # на последней попытке температура 0.7


def get_structured_llm(
    pydantic_model: Type[BaseModel], attempt_number: int
) -> ChatOpenAI:
    """
    Возвращает LLM, настроенный на возврат указанной Pydantic-модели
    и настройками температуры, которая увеличивается с номером попытки.

    Args:
        pydantic_model: Класс Pydantic-модели для structured_output.
        attempt_number: Номер попытки (1..MAX_ATTEMPTS).

    Returns:
        подключение к llm с .with_structured_output(pydantic_model)
    """
    if not (1 <= attempt_number <= MAX_ATTEMPTS):
        raise ValueError(f"Номер попытки должен быть от 1 до {MAX_ATTEMPTS}")

    # Рассчитываем температуру: от 0.0 до 0.7
    temperature = 0.0 + (FINAL_TEMPERATURE * (attempt_number - 1)) / (MAX_ATTEMPTS - 1)
    temperature = round(temperature, 2)

    # Загружаем переменные окружения
    load_dotenv()

    api_base = os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")

    # if not api_base or not api_key or not model_name:
    #     raise ValueError("Не видно переменные окружения")

    # Инициализируем LLM с нужной температурой
    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=api_base,
        temperature=temperature,
    )
    
    # llm = ChatMistralAI(
    #     model_name = model_name,
    #     api_key = api_key,
    #     temperature = temperature
    # )
    print(f"Температура: {temperature}")

    return llm.with_structured_output(pydantic_model)  # Добавляем pydantic модель к llm (запросу)
