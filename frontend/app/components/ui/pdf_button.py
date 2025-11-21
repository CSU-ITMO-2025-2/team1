"""Компонент кнопки экспорта в PDF."""

import streamlit as st

from frontend.app.utils.pdf_export import PDF_ICON, pdf_file_name


def pdf_download_button(
    namespace: str,
    label: str,
    pdf_bytes: bytes,
    mode: str = "view",
) -> bool:
    """Отображает кнопку экспорта в PDF.

    Args:
        namespace: Пространство имен для ключей
        label: Метка для имени файла
        pdf_bytes: Байты PDF файла
        mode: Режим отображения ("view" или "edit")

    Returns:
        True если PDF был скачан, иначе False

    """
    help_text = "Экспортировать в PDF" if mode == "view" else "Экспорт текущей редакции в PDF"
    key_suffix = "pdf_view" if mode == "view" else "pdf_edit"

    pdf_clicked = st.download_button(
        "",
        data=pdf_bytes,
        file_name=pdf_file_name(label),
        mime="application/pdf",
        type="secondary",
        key=f"{namespace}:{key_suffix}",
        help=help_text,
        icon=PDF_ICON,
        use_container_width=False,
    )
    if pdf_clicked:
        st.toast(f"Секция «{label}»: PDF выгружен")
        return True
    return False

