"""Компонент для отображения результатов генерации описания вакансии."""

import streamlit as st

from frontend.app.components.ui.button_panel import get_button_panel


def render_job_description_results(
    result: dict,
    namespace: str,
) -> None:
    """Рендерит результаты генерации описания вакансии в виде вкладок.

    Args:
        result: Словарь с результатами генерации (job_site, job_flyer_format, etc.)
        namespace: Namespace для ключей session_state

    """

    def k(name: str) -> str:
        return f"{namespace}:{name}"

    tabs = st.tabs(["Сайт", "Флаер", "ТВ/газета", "Соцсети"])
    slots = {
        "Сайт": "job_site",
        "Флаер": "job_flyer_format",
        "ТВ/газета": "job_media_format",
        "Соцсети": "job_social_media_format",
    }
    section_titles = {
        "Сайт": "Описание для рабочего сайта",
        "Флаер": "Описание для флаера",
        "ТВ/газета": "Описание для ТВ / газеты",
        "Соцсети": "Описание для соцсетей",
    }

    # Подготавливаем все секции для PDF (все вкладки)
    all_sections = []
    for label, slot_key in slots.items():
        text = result.get(slot_key, "")
        if text and text.strip():
            all_sections.append(
                {
                    "id": label,
                    "title": section_titles.get(label, label),
                    "text": text,
                }
            )

    for tab, label in zip(tabs, slots, strict=False):
        with tab:
            slot_key = slots[label]
            text = result.get(slot_key, "Не получен результат генерации")

            # Используем все секции для PDF, но текущую секцию для отображения
            updated = get_button_panel(
                pdf_sections=all_sections,
                text=text,
                namespace_state=namespace,
                current_section_id=label,
                pdf_filename="Описание вакансии",
            )
            st.session_state[k("result")][slot_key] = updated
