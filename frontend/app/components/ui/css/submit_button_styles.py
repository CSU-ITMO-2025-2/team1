"""Стили для форм ввода."""

import streamlit as st


def inject_submit_button_styles() -> None:
    """Инжектит CSS стили для кнопки submit формы.
    Используется для фиксации размеров кнопки отправки формы.
    """
    st.markdown(
        """
        <style>
        :root { --btn-h: 44px; --btn-w: 240px; }

        /* 1) Целимся ровно в submit-кнопку формы по data-testid (Emotion-классы не трогаем) */
        div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]{
          width: var(--btn-w) !important;
          height: var(--btn-h) !important;
          min-height: var(--btn-h) !important;
          max-height: var(--btn-h) !important;
          line-height: var(--btn-h) !important;   /* вертикальный центр текста */
          padding-block: 0 !important;
          box-sizing: border-box !important;
        }

        /* 2) Одинаковая высота во всех состояниях */
        div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:disabled,
        div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:hover,
        div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:active,
        div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:focus-visible{
          height: var(--btn-h) !important;
          min-height: var(--btn-h) !important;
          max-height: var(--btn-h) !important;
          line-height: var(--btn-h) !important;
          outline: none !important;
          box-shadow: none !important;
          border-width: 1px !important;
        }

        /* 3) Внутренний Markdown-контейнер: без внешних отступов и без переноса строк */
        div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]
          div[data-testid="stMarkdownContainer"] p{
          margin: 0 !important;
          white-space: nowrap !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
