"""Утилиты для работы с загруженными файлами."""

import io
from typing import Optional
import fitz
from docx import Document
import streamlit as st


def extract_text_from_file(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> Optional[str]:
    """
    Извлекает текст из загруженного файла (PDF, DOCX, TXT).
    
    Args:
        uploaded_file: Загруженный файл Streamlit
    
    Returns:
        Извлеченный текст или None при ошибке
    """
    if not uploaded_file:
        return None
    
    data = uploaded_file.getvalue()
    name = (uploaded_file.name or "").lower()
    
    if name.endswith(".txt"):
        try:
            return data.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            return None
    
    if name.endswith(".docx"):
        try:
            document = Document(io.BytesIO(data))
            return "\n".join(p.text for p in document.paragraphs if p.text)
        except Exception:
            return None
    
    if name.endswith(".pdf"):
        try:
            pdf = fitz.open(stream=data, filetype="pdf")
            text = "\n".join(page.get_text() for page in pdf)
            pdf.close()
            return text
        except (fitz.FileDataError, RuntimeError, ValueError):
            return None
    
    return None


def compose_case_input_text(
    mode: str,
    text_value: Optional[str],
    uploaded_file: Optional[st.runtime.uploaded_file_manager.UploadedFile],
    resume_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None
) -> str:
    """
    Формирует текстовый блок с исходными данными заявки.
    
    Args:
        mode: Режим ввода ("Текст" или "Файл")
        text_value: Текстовое значение (если mode == "Текст")
        uploaded_file: Загруженный файл (если mode == "Файл")
        resume_file: Дополнительный файл резюме (опционально, для оценки резюме)
    
    Returns:
        Строка с исходными данными для отображения
    """
    if mode == "Текст":
        return (text_value or "").strip()
    
    if not uploaded_file:
        return "Файл с описанием не был загружен."
    
    extracted = extract_text_from_file(uploaded_file)
    header = f"Файл: {uploaded_file.name}"
    if extracted:
        result = f"{header}\n\n{extracted.strip()}"
    else:
        result = f"{header}\n\n(Не удалось извлечь содержимое файла.)"
    
    # Добавляем второй файл, если он есть
    if resume_file:
        resume_extracted = extract_text_from_file(resume_file)
        resume_header = f"\n\n---\n\nФайл резюме: {resume_file.name}"
        if resume_extracted:
            result += f"{resume_header}\n\n{resume_extracted.strip()}"
        else:
            result += f"{resume_header}\n\n(Не удалось извлечь содержимое файла.)"
    
    return result

