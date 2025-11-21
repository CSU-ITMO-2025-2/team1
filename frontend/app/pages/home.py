"""Главная страница приложения HR-Assist."""

import streamlit as st

st.set_page_config(
    page_title="HR-Assist - Главная",
    page_icon="🏠",
    layout="wide",
)

from components.general.profile_button import render_profile_button
from components.general.sidebar import render_sidebar
from components.home.header import render_main_header
from components.home.service_cards import render_service_cards
from services.auth_client import load_user_once

# Дизайн вкладок
render_sidebar()

# Рендерим компоненты страницы
render_profile_button()
render_main_header()
render_service_cards()

# Загружаем информацию о пользователе при первом рендере
if "user" not in st.session_state:
    load_user_once()
