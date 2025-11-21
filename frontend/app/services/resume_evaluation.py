import json
import os
from typing import Dict, Optional
import requests
from requests_toolbelt import MultipartEncoder
import streamlit as st

CORE_API_HOST = os.getenv("CORE_API_HOST")
CORE_API_PORT = os.getenv("CORE_API_PORT")

BASE_URL = f"http://{CORE_API_HOST}:{CORE_API_PORT}"


def resume_evaluation(
    vacancy_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None,
    resume_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None
) -> Dict:
    """
    POST /resume_evaluation
    Отправляет текст и/или файлы для оценки резюме.

    Args:
        vacancy_file: Файл с вакансией (опционально)
        resume_file: Файл с резюме (опционально)

    Returns:
        JSON-ответ API как dict
    """
    url = f"{BASE_URL}/resume_evaluation"

    # Формируем multipart/form-data запрос
    fields = {}

    if vacancy_file:
        fields['vacancy_file'] = (vacancy_file.name, vacancy_file.getvalue(), vacancy_file.type or 'application/octet-stream')
    if resume_file:
        fields['resume_file'] = (resume_file.name, resume_file.getvalue(), resume_file.type or 'application/octet-stream')

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

    encoder = MultipartEncoder(fields=fields)
    headers = {'Content-Type': encoder.content_type}
    resp = requests.post(url, data=encoder, headers=headers)

    resp.raise_for_status()
    return resp.json()
