"""Карточки на главной странице"""

import streamlit as st


def render_service_cards():
    """Рендерит три карточки-ссылки на сервисы с кастомными стилями через ключи."""
    # Описываем карточки: (label, иконка, путь страницы, уникальный key)
    cards = [
        ("Описание вакансии", "📝", "pages/job_description.py", "describe"),
        ("Оценка резюме", "📊", "pages/resume_evaluation.py", "evaluate"),
        (
            "Генерация вопросов кандидату",
            "❓",
            "pages/questions_generation.py",
            "questions",
        ),
    ]

    # CSS для стилизации кнопок-карточек
    css = "<style>\n"
    for _label, _icon, _page, key in cards:
        css += f"""
        /* Стили для карточки с key='{key}' */
        .st-key-{key} .stButton>button {{
            background-color: #f0f8ff !important;
            border: none !important;
            border-radius: 15px !important;
            padding: 20px !important;
            width: 240px !important;
            height: 140px !important;
            font-size: 1.6rem !important;
            font-weight: 800 !important;
            line-height: 1.4 !important;
            text-align: left !important;
            display: flex !important;
            align-items: center !important;
            gap: 15px !important;
            cursor: pointer !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
            transition: background-color 0.2s, transform 0.2s !important;
        }}
        .st-key-{key} .stButton>button:hover {{
            background-color: #e1f0ff !important;
            transform: translateY(-3px) !important;
        }}
        """
    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)

    # Горизонтальный flex-контейнер с переносом и равномерными отступами
    row = st.container(horizontal=True, horizontal_alignment="left", gap="large")

    for label, icon, page, key in cards:
        with row:
            # можно обернуть в контейнер, чтобы держать ширину/высоту
            box = st.container(border=False, width=260, height="content")
            with box:
                if st.button(f"{icon} {label}", key=key):
                    # Программный переход на страницу внутри multipage
                    st.switch_page(page)
