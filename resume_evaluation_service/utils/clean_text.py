"""Вспомогательные функции для очистки текста."""

from typing import List, Union

def clean_text(text: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    Убирает проблемные невидимые символы из текста.
    Работает как со строками, так и со списками строк.
    """
    if isinstance(text, list):
        # Если передан список, очищаем каждый элемент
        return [clean_single_text(item) for item in text]
    elif isinstance(text, str):
        # Если передана строка, очищаем её
        return clean_single_text(text)
    else:
        # Если другой тип данных, возвращаем как есть
        return text


def clean_single_text(text: str) -> str:
    """
    Убирает проблемные невидимые символы из одиночной строки.
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""

    return (
        text.replace("\u202f", " ")  # Narrow No-Break Space
        .replace("\u00a0", " ")  # Non-breaking space
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("\t", " ")
        .replace("\f", " ")
        .replace("\v", " ")
        .replace(" ", " ")  # Another NBSP
        .strip()
    )
