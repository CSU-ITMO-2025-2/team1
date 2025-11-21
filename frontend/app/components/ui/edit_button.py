"""Компонент кнопки редактирования."""

import streamlit as st


def edit_button(
    namespace: str,
    text: str,
    work_key: str,
    edit_key: str,
    notify_key: str,
) -> bool:
    """Отображает кнопку редактирования.

    Args:
        namespace: Пространство имен для ключей
        text: Текущий текст для редактирования
        work_key: Ключ для рабочего текста в session_state
        edit_key: Ключ для состояния редактирования
        notify_key: Ключ для уведомлений

    Returns:
        True если кнопка была нажата, иначе False

    """
    if st.button(
        "",
        icon=":material/edit:",
        type="secondary",
        help="Редактировать",
        key=f"{namespace}:edit",
        use_container_width=False,
    ):
        st.session_state[work_key] = text
        st.session_state[edit_key] = True
        st.session_state[notify_key] = "Режим редактирования включён"
        st.toast("Режим редактирования включён")
        st.rerun()
        return True
    return False

