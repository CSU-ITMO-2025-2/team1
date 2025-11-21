"""
Страница профиля пользователя.
"""

import streamlit as st

# Конфигурация страницы
st.set_page_config(page_title="HR-Assist - Профиль", page_icon="👤", layout="wide")

from services.auth_client import load_user_once, login_link
from components.general.sidebar import render_sidebar

# Дизайн вкладок
render_sidebar()


def _display_name(user: dict) -> str:
    """
    Получение отображаемого имени пользователя.

    Args:
        user: Данные пользователя

    Returns:
        Отображаемое имя
    """
    if user.get("name"):
        return user.get("name")
    if user.get("given_name") and user.get("family_name"):
        return f"{user.get('family_name')} {user.get('given_name')}"
    if user.get("preferred_username"):
        return user.get("preferred_username")
    if user.get("email"):
        return user.get("email").split("@")[0]
    return user.get("sub", "Пользователь")


# Стили для кнопок
st.markdown(
    """
<style>
.auth-btn{
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    padding: .5rem 1rem;
    background: #fff;
    color: #0057A0;
    border: 2px solid #0057A0;
    border-radius: 12px;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.2s;
}
.auth-btn:hover{
    background: #E5F0FF;
}
.logout-btn{
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    padding: .5rem 1rem;
    background: #fff;
    color: #d32f2f;
    border: 2px solid #d32f2f;
    border-radius: 12px;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.2s;
}
.logout-btn:hover{
    background: #ffebee;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Личный кабинет")

# 1) Поднимаем пользователя
user = load_user_once()

# 2) Если не авторизован — предлагаем войти
if not user:
    st.info("Для доступа к личному кабинету необходимо авторизоваться.")
    st.html(f'<a class="auth-btn" href="{login_link("/pages/profile")}">🔐 Войти</a>')
    st.caption("После входа вы вернётесь на эту страницу.")
    st.stop()

# 3) Если авторизован, но нет доступа по группам — мягко откажем
has_access = bool(user.get("has_access"))
if not has_access:
    st.warning("У вас нет доступа к личному кабинету. Обратитесь к администратору для добавления в нужную группу.")
    # Можно подсветить, какие разрешённые группы у пользователя (скорее всего пусто)
    allowed_groups = user.get("groups") or []
    if allowed_groups:
        st.write("Ваши разрешённые группы:", ", ".join(allowed_groups))
    col_l, col_r = st.columns([1, 1])
    # with col_l:
    #     if st.button("← На главную", use_container_width=True):
    #         st.switch_page("pages/home.py")
    # with col_r:
    #     st.html(f'<a class="logout-btn" href="{logout_link()}">🚪 Выйти</a>')
    # st.stop()

full_name = user.get("name")

parts = [p.strip() for p in full_name.split() if p.strip()]
    
    
# Берем первую часть (фамилию)
result_name = f"{parts[0]} {parts[1]}"


# 4) Допуск есть — показываем профиль
st.subheader(f"👤 {result_name}")

col1, col2 = st.columns(2)
with col1:
    st.write("**Логин:**", user.get("preferred_username", "—"))
    st.write("**Email:**", user.get("email", "—"))

with col2:
    # Backend уже вернул пересечение разрешённых групп
    allowed_groups = user.get("groups") or []
    if allowed_groups:
        st.write("**Доступные роли:**", ", ".join(allowed_groups))
    else:
        st.write("**Доступные роли:** —")

st.divider()

# # Кнопка выхода
# st.html(f'<a class="logout-btn" href="{logout_link()}">🚪 Выйти из системы</a>')

# # Кнопка возврата на главную
# if st.button("← Вернуться на главную", type="secondary"):
#     st.switch_page("pages/home.py")
