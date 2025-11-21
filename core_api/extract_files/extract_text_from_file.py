"""
Утилиты для работы с файлами
"""
import io
from typing import Optional
from fastapi import UploadFile, HTTPException

async def file_to_text(uploaded: UploadFile) -> Optional[str]:
    """
    Возвращает текст из загруженного файла .txt / .docx / .pdf.
    Для .docx используем python-docx, для .pdf — PyMuPDF (fitz).

    Args:
        uploaded: Загруженный файл через FastAPI

    Returns:
        str: Извлеченный текст или None при ошибке

    Raises:
        HTTPException: При ошибках обработки файла
    """
    if not uploaded or not uploaded.filename:
        return None

    name = uploaded.filename.lower()

    try:
        # Читаем содержимое файла
        content = await uploaded.read()
        await uploaded.seek(0)  # Возвращаем указатель в начало

        # .txt — читаем как utf-8
        if name.endswith(".txt"):
            try:
                return content.decode("utf-8", errors="ignore")
            except Exception:
                return None

        # .docx — через python-docx
        if name.endswith(".docx"):
            try:
                from docx import Document  # python-docx
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="Для чтения .docx не установлен пакет python-docx"
                )

            try:
                doc_stream = io.BytesIO(content)
                doc = Document(doc_stream)
                return "\n".join(p.text for p in doc.paragraphs)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Не удалось прочитать DOCX: {e}"
                )

        # .pdf — через PyMuPDF (fitz)
        if name.endswith(".pdf"):
            try:
                import fitz  # PyMuPDF
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="Для чтения .pdf не установлен пакет PyMuPDF (pymupdf)"
                )

            try:
                pdf = fitz.open(stream=content, filetype="pdf")
                text = "\n".join(page.get_text() for page in pdf)
                pdf.close()
                return text
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Не удалось прочитать PDF: {e}"
                )

        # неизвестный формат
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла: {name}"
        )

    except HTTPException:
        # Перебрасываем HTTPException как есть
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке файла: {str(e)}"
        )
