import json
import os
from typing import Optional
import requests
from requests_toolbelt import MultipartEncoder
import streamlit as st

# URL API-сервера
CORE_API_HOST = os.getenv("CORE_API_HOST")
CORE_API_PORT = os.getenv("CORE_API_PORT")

BASE_URL = f"http://{CORE_API_HOST}:{CORE_API_PORT}"

def get_vacancy_description(
    input_data: Optional[str] = None,
    input_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None
) -> dict:
    """
    Отправляет POST-запрос к эндпоинту /generate_vacancy_description

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
    url = f"{BASE_URL}/generate_vacancy_description"

    # Формируем multipart/form-data запрос
    fields = {}

    if input_data:
        fields['input_data'] = input_data
    if input_file:
        fields['input_file'] = (input_file.name, input_file.getvalue(), input_file.type or 'application/octet-stream')

    # Добавляем данные пользователя (если авторизован)
    user = st.session_state.get("user")
    if user:
        user_data = {
            "auth_provider": "keycloak",
            "external_id": user.get("sub"),
            "email": user.get("email"),
            "full_name": user.get("name")
        }
        fields['user_data'] = json.dumps(user_data)

    # Если есть файл, используем multipart
    if input_file:
        encoder = MultipartEncoder(fields=fields)
        headers = {'Content-Type': encoder.content_type}
        response = requests.post(url, data=encoder, headers=headers)
    else:
        # Если только текст, отправляем как form data
        response = requests.post(url, data=fields)

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
