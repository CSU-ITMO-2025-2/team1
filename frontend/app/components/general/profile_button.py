"""
Компонент кнопки профиля с индикацией авторизации.
"""

import streamlit as st
from services.auth_client import (
    login_link,
    get_compact_name,
)


def render_profile_button():
    """Кнопка профиля с индикацией статуса авторизации."""

    # Стили для кнопки и блока авторизации
    st.markdown("""
    <style>
    /* Кнопка профиля - фиксированное позиционирование */
    .st-key-profile_button.element-container{
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        z-index: 1000 !important;
    }

    .st-key-profile_button.element-container button{
        width: 48px !important;
        height: 48px !important;
        background: #fff !important;
        border: 2px solid #0057A0 !important;
        border-radius: 12px !important;
        font-size: 1.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
    }

    .st-key-profile_button.element-container button:hover{
        background: #E5F0FF !important;
    }

    /* Блок слева от профиля */
    #auth-under{
        position: fixed;
        top: 20px;
        right: calc(20px + 48px + 12px);  /* отступ = правый отступ + ширина кнопки + зазор */
        z-index: 1000;
        display: flex;
        gap: 8px;
        align-items: center;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial;
    }

    /* Кнопка "Войти" */
    #auth-under a.auth-btn{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        height: 48px;
        padding: 0 14px;
        background: #fff;
        color: #0057A0;
        text-decoration: none;
        font-weight: 600;
        border: 2px solid #0057A0;
        border-radius: 12px;
        transition: background 0.2s;
    }

    #auth-under a.auth-btn:hover{
        background: #E5F0FF;
    }

    /* Плашка с ФИО */
    #auth-under .name{
        display: inline-flex;
        align-items: center;
        height: 48px;
        padding: 0 12px;
        background: #fff;
        color: #0b2540;
        font-weight: 600;
        white-space: nowrap;
        border: 2px solid #0057A0;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Загружаем информацию о пользователе
    user = st.session_state.get("user")

    # Кнопка профиля - всегда отображается
    if st.button("👤", help="Личный кабинет рекрутера",
                 key="profile_button", use_container_width=False):
        st.switch_page("pages/profile.py")

    # Индикация статуса авторизации
    if not user:
        # Показываем кнопку "Войти"
        st.html(
            f"""
            <div id="auth-under">
              <a class="auth-btn" href="{login_link()}">Войти</a>
            </div>
            """
        )
    else:
        # Показываем имя пользователя
        name = user.get("name") or user.get("preferred_username") or user.get("email") or "Пользователь"
        compact = get_compact_name(name)
        st.html(
            f"""
            <div id="auth-under">
              <span class="name">{compact}</span>
            </div>
            """
        )
