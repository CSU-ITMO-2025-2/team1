"""Функции для работы с маркдаун объектами."""

from collections.abc import Callable

import streamlit as st

from frontend.app.components.ui.cancel_button import cancel_button
from frontend.app.components.ui.copy_button import copy_icon
from frontend.app.components.ui.css.button_panel_styles import (
    inject_button_panel_styles,
    inject_md_card_styles,
)
from frontend.app.components.ui.edit_button import edit_button
from frontend.app.components.ui.pdf_button import pdf_download_button
from frontend.app.components.ui.reset_button import reset_button
from frontend.app.components.ui.save_button import save_button
from frontend.app.utils.pdf_export import build_pdf_bytes, normalize_md

# Константы
DEFAULT_HEIGHT = 700
DEFAULT_TONE = "neutral"
DEFAULT_RESET_LABEL = "Очистить результат"
DEFAULT_LABEL = "Результат"


def md_card(text: str, height: int = 720, tone: str = "neutral", title: str = "") -> None:
    """Контейнер для маркдаун с кнопкой копирования."""
    with st.container(border=True):
        # Создаем контейнер для заголовка и кнопки с фиксированными размерами
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            # Заголовок слева
            if title:
                st.markdown(f"**{title}**")
        with col2:
            # Кнопка копирования справа
            copy_icon(
                normalize_md(text),
                key="md_card_copy",
                tooltip="Скопировать",
                label="",
                icon_variant="material_symbols",
            )
        # Отображаем отрендеренный markdown
        st.markdown(normalize_md(text))
    inject_md_card_styles(height=height, tone=tone)


def _get_editing_state(
    namespace: str,
    initial_text: str,
) -> tuple[str, str, str, bool]:
    """Инициализирует и возвращает ключи состояния редактирования."""
    txt_key = f"{namespace}:text"
    edit_key = f"{namespace}:editing"
    work_key = f"{namespace}:work"

    st.session_state.setdefault(txt_key, initial_text)
    st.session_state.setdefault(edit_key, False)
    st.session_state.setdefault(work_key, st.session_state[txt_key])

    return txt_key, edit_key, work_key, st.session_state[edit_key]


def _build_pdf_payload(
    current_text: str,
    label: str,
    case_input: str | None,
    pdf_sections: list[dict[str, str]] | None,
) -> bytes:
    """Строит payload для PDF экспорта."""
    sections_payload: list[tuple[str, str]] = []
    if pdf_sections:
        seen = False
        for section in pdf_sections:
            section_id = section.get("id") or section.get("title") or label
            display_title = section.get("title") or section_id
            body = section.get("text", "")
            if section_id == label:
                body = current_text
                seen = True
            sections_payload.append((display_title, body))
        if not seen:
            sections_payload.append((label, current_text))
    else:
        sections_payload = [(label, current_text)]

    base_context = case_input if (case_input is not None and case_input.strip()) else current_text
    return build_pdf_bytes(base_context, sections_payload)


def _render_view_left_buttons(
    namespace: str,
    text: str,
    work_key: str,
    edit_key: str,
    notify_key: str,
) -> None:
    """Рендерит левые кнопки в режиме просмотра."""
    with st.container(border=False, horizontal=True, horizontal_alignment="left", gap="small"):
        edit_button(namespace, text, work_key, edit_key, notify_key)


def _render_view_right_buttons(
    namespace: str,
    label: str,
    pdf_bytes: bytes,
    reset_label: str | None,
    on_reset: Callable[[], None] | None,
    pdf_filename: str | None = None,
) -> None:
    """Рендерит правые кнопки в режиме просмотра."""
    pdf_download_button(namespace, pdf_filename or label, pdf_bytes, mode="view")
    if reset_label and on_reset:
        reset_button(namespace, reset_label, on_reset, mode="view")


def _render_edit_left_buttons(
    namespace: str,
    work_key: str,
    txt_key: str,
    edit_key: str,
) -> None:
    """Рендерит левые кнопки в режиме редактирования."""
    save_button(namespace, work_key, txt_key, edit_key)
    cancel_button(namespace, work_key, txt_key, edit_key)


def _render_edit_right_buttons(
    namespace: str,
    label: str,
    pdf_bytes: bytes,
    reset_label: str | None,
    on_reset: Callable[[], None] | None,
    pdf_filename: str | None = None,
) -> None:
    """Рендерит правые кнопки в режиме редактирования."""
    with st.container(horizontal=True, gap="small", horizontal_alignment="right"):
        pdf_download_button(namespace, pdf_filename or label, pdf_bytes, mode="edit")
        if reset_label and on_reset:
            reset_button(namespace, reset_label, on_reset, mode="edit")


def _render_markdown_view(text: str, height: int, tone: str, title: str = "") -> None:
    """Рендерит карточку с markdown текстом."""
    md_card(text, height=height, tone=tone, title=title)


def _render_text_editor(work_key: str, height: int) -> None:
    """Рендерит текстовое поле для редактирования."""
    with st.container(border=True):
        st.text_area("Текст вакансии", key=work_key, height=height - 100)


def get_button_panel(
    pdf_sections: list[dict[str, str]],
    text: str,
    namespace_state: str,
    *,
    height: int = DEFAULT_HEIGHT,
    tone: str = DEFAULT_TONE,
    reset_label: str = DEFAULT_RESET_LABEL,
    case_input_key: str | None = None,
    result_key: str | None = None,
    uploader_key: str | None = None,
    current_section_id: str | None = None,
    pdf_filename: str | None = None,
) -> str:
    """Панель кнопок для просмотра и редактирования markdown с экспортом в PDF.

    Args:
        pdf_sections: Список секций для PDF-экспорта
        text: Текст для отображения
        namespace_state: Пространство имен для состояния (например, "jobdesc", "questions")
        height: Высота карточки
        tone: Тон карточки ("neutral", "blue", "green")
        reset_label: Текст подсказки для кнопки сброса
        case_input_key: Ключ для исходных данных в session_state (по умолчанию "{namespace_state}:case_input_text")
        result_key: Ключ для результата в session_state (по умолчанию "{namespace_state}:result")
        uploader_key: Ключ для счетчика загрузчика в session_state (по умолчанию "{namespace_state}:uploader_key")
        current_section_id: ID текущей секции (если не указан, берется из первой секции pdf_sections)
        pdf_filename: Имя файла для PDF экспорта (если не указано, используется current_section_id или label)

    Returns:
        Актуальный текст (отредактированный или оригинальный)

    """
    # Инициализация
    # Используем current_section_id если передан, иначе берем из первой секции
    label = current_section_id or (pdf_sections[0]["id"] if pdf_sections else DEFAULT_LABEL)
    namespace = f"{namespace_state}:{label}"
    notify_key = f"{namespace}:notify"

    # Определение ключей для состояния
    case_input_key = case_input_key or f"{namespace_state}:case_input_text"
    result_key = result_key or f"{namespace_state}:result"
    uploader_key = uploader_key or f"{namespace_state}:uploader_key"

    case_input = st.session_state.get(case_input_key, "")

    def reset_callback() -> None:
        st.session_state[result_key] = None
        if uploader_key in st.session_state:
            st.session_state[uploader_key] += 1
        st.session_state[case_input_key] = ""
        st.toast("Результат очищен")
        st.rerun()

    # Инициализация стилей
    inject_button_panel_styles()

    # Обработка уведомлений
    pending_notice = st.session_state.pop(notify_key, None)
    if pending_notice:
        st.toast(pending_notice)

    # Получение состояния редактирования
    txt_key, edit_key, work_key, is_editing = _get_editing_state(namespace, text)

    # Контейнер с кнопками - обернут в контейнер с border для соответствия ширине блока результатов
    with st.container(border=False):
        row = st.container(
            horizontal=True,
            horizontal_alignment="distribute",
        )

        if not is_editing:
            # Режим просмотра
            with row:
                _render_view_left_buttons(
                    namespace,
                    st.session_state[txt_key],
                    work_key,
                    edit_key,
                    notify_key,
                )

                st.space("stretch")

                pdf_bytes = _build_pdf_payload(
                    st.session_state[txt_key],
                    label,
                    case_input,
                    pdf_sections,
                )

                _render_view_right_buttons(
                    namespace,
                    label,
                    pdf_bytes,
                    reset_label,
                    reset_callback,
                    pdf_filename,
                )

        else:
            # Режим редактирования
            with row:
                _render_edit_left_buttons(namespace, work_key, txt_key, edit_key)

                st.space("stretch")

                pdf_bytes = _build_pdf_payload(
                    st.session_state[work_key],
                    label,
                    case_input,
                    pdf_sections,
                )
                _render_edit_right_buttons(
                    namespace,
                    label,
                    pdf_bytes,
                    reset_label,
                    reset_callback,
                    pdf_filename,
                )

    if not is_editing:
        _render_markdown_view(st.session_state[txt_key], height, tone, title=label)
        return st.session_state[txt_key]
    _render_text_editor(work_key, height)
    return st.session_state[work_key]
