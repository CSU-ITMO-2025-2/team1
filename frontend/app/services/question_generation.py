import os
from typing import Dict
import requests
import streamlit as st

from utils.file_utils import extract_text_from_file
from utils.cookie_utils import prepare_request_cookies

CORE_API_HOST = os.getenv("CORE_API_HOST")
CORE_API_PORT = os.getenv("CORE_API_PORT")

BASE_URL = f"http://{CORE_API_HOST}:{CORE_API_PORT}"


def question_generation(
    vacancy_file: st.runtime.uploaded_file_manager.UploadedFile,
    resume_file: st.runtime.uploaded_file_manager.UploadedFile
) -> Dict:
    """
    POST /questions/generate
    Отправляет текст вакансии и резюме для генерации вопросов для интервью.

    Args:
        vacancy_file: Файл с вакансией
        resume_file: Файл с резюме

    Returns:
        JSON-ответ API как dict
    """
    url = f"{BASE_URL}/questions/generate"

    # Извлекаем текст из файлов
    vacancy_text = extract_text_from_file(vacancy_file)
    resume_text = extract_text_from_file(resume_file)

    # Формируем JSON запрос
    payload = {
        "vacancy_text": vacancy_text,
        "resume_text": resume_text,
    }

    # Получаем cookies для авторизации
    cookies = prepare_request_cookies()

    # Отправляем JSON с cookies
    response = requests.post(url, json=payload, cookies=cookies)
    response.raise_for_status()
    
    return response.json()
