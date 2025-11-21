"""
Компонент заголовка главной страницы.
"""

import streamlit as st
from services.auth_client import load_user_once


def render_main_header():
    """
    Рендерит основной заголовок с персональным приветствием.
    """
    # Получаем информацию о пользователе
    user = st.session_state.get("user")

    if user:
        # Получаем имя для приветствия
        # Приоритет:  первое слово из name > preferred_username
        greeting_name = None

        if user.get("name"):
            # Берем первое имя (обычно это имя, а не фамилия)
            parts = user.get("name", "").strip().split()
            if len(parts) >= 2:
                greeting_name = parts[1]  # Второе слово (имя)
            elif parts:
                greeting_name = parts[0]  # Если только одно слово
        elif user.get("preferred_username"):
            greeting_name = user.get("preferred_username")

        if greeting_name:
            st.title(f"Добрый день, {greeting_name}!")
        else:
            st.title("Добрый день!")
    else:
        st.title("Добрый день!")

    st.write("")  # Отступ
    st.subheader("Сервисы")
