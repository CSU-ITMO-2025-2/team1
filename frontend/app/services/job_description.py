import os
from typing import Optional
import requests
import streamlit as st

from utils.file_utils import extract_text_from_file
from utils.cookie_utils import prepare_request_cookies

# URL API-сервера
CORE_API_HOST = os.getenv("CORE_API_HOST")
CORE_API_PORT = os.getenv("CORE_API_PORT")

BASE_URL = f"http://{CORE_API_HOST}:{CORE_API_PORT}"


def get_vacancy_description(
    input_data: Optional[str] = None,
    input_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None
) -> dict:
    """
    Отправляет POST-запрос к эндпоинту /job_description/generate

    Args:
        input_data: Текст с описанием (опционально)
        input_file: Файл с описанием (опционально)

    Returns:
        Словарь с ключами:
        - job_site: описание для сайта
        - job_flyer_format: текст для флаера
        - job_media_format: текст для ТВ/газета
        - job_social_media_format: текст для соцсетей
    """
    url = f"{BASE_URL}/job_description/generate"

    # Получаем текст из файла или используем переданный текст
    if input_file:
        text = extract_text_from_file(input_file)
    elif input_data:
        text = input_data
    else:
        raise ValueError("Необходимо указать input_data или input_file")

    # Формируем JSON запрос
    payload = {
        "input_data": text,
    }

    # Получаем cookies для авторизации
    cookies = prepare_request_cookies()

    # Отправляем JSON с cookies
    response = requests.post(url, json=payload, cookies=cookies)
    response.raise_for_status()
    result = response.json()

    status = result.get("status")
    if status != "success":
        raise RuntimeError(f"API returned error status: {status}")

    data = result.get("data")
    if not isinstance(data, dict):
        raise ValueError("API response 'data' is not a dict")

    # Извлекаем необходимые поля
    return {
        "job_site": data.get("job_site", ""),
        "job_flyer_format": data.get("job_flyer_format", ""),
        "job_media_format": data.get("job_media_format", ""),
        "job_social_media_format": data.get("job_social_media_format", ""),
    }
