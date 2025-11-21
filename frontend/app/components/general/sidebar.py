"""Боковая панель сервиса"""

import streamlit as st


def render_sidebar():
    """Рендерит боковую панель на каждой странице"""
    # # Рендерим лого
    # st.logo(
    #     "frontend/app/assets/favicon.png",  # URL или путь к локальному файлу
    #     size="large",
    #     link=None,  # ссылка при клике (по желанию)
    #     icon_image=None,  # иконка при закрытом sidebar
    # )

    # Стили для sidebar
    st.markdown(
        """
        <style>
        /* Фон и отступ sidebar */
        section[data-testid="stSidebar"] {
        background-color: #0550A0 !important;
        padding-top: 1rem !important;
        width: 320px !important;
        color: white;
        }

        /* Цвет текста в сайдбаре */
        [data-testid="stSidebarContent"] {
            color: #FFFFFF !important;
        }

        /* Скрываем шапку приложения */
        header[data-testid="stHeader"] {
            display: none !important;
        }

        /* Все надписи ссылок в sidebar (Главная/Профиль/Сервисы/…) */
        div[data-testid="stSidebarNav"] 
        a[data-testid="stSidebarNavLink"] > span {
            color: #FFFFFF !important;
            font-size: 1.05rem !important;     /* увеличиваем шрифт */
        }
        /* Для секций (заголовков групп) */
        header[data-testid="stNavSectionHeader"] span {
            color: #FFFFFF !important;
            font-size: 1.1rem !important;    /* чуть крупнее */
            font-weight: 300 !important;      /* опционально: сделать полужирным */
        }

        /* Делаем контейнер flex и position:relative */
        [data-testid="stSidebarHeader"] {
        display: flex !important;
        align-items: center !important;
        position: relative !important;
        padding: 0.5rem 1rem !important;
        gap: 0.1rem !important;
        }
        /* Скрываем стандартный spacer и кнопку-свёртку */
        [data-testid="stSidebarHeader"] [data-testid="stLogoSpacer"],
        [data-testid="stSidebarHeader"] [data-testid="stSidebarCollapseButton"] {
        display: none !important;
        }
        /* ::after — название сервиса с отступом слева */
        [data-testid="stSidebarHeader"]::after {
        content: "HR-Assistant" !important;         
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        }
        
        /* белый квадрат под логотип */
        [data-testid="stSidebarHeader"] img {
        /* задаём размеры самого квадрата (ширина + padding) */
        background-color: #FFFFFF !important; /* белый фон */
        border-radius: 12px !important;       /* скруглённые углы */
        padding: 6px !important;              /* отступ внутри квадрата */
        box-sizing: content-box !important;   /* чтобы padding увеличивал фон */

        /* фиксированный размер итогового контейнера */
        width: 45px !important;
        height: 45px !important;
        /* убедимся, что картинка внутри остаётся по центру */
        object-fit: contain !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
