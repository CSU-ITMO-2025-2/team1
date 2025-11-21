"""Компонент кнопки сброса."""

from collections.abc import Callable

import streamlit as st


def reset_button(
    namespace: str,
    reset_label: str,
    on_reset: Callable[[], None],
    mode: str = "view",
) -> bool:
    """Отображает кнопку сброса.

    Args:
        namespace: Пространство имен для ключей
        reset_label: Текст подсказки для кнопки
        on_reset: Функция обратного вызова при нажатии
        mode: Режим отображения ("view" или "edit")

    Returns:
        True если кнопка была нажата, иначе False

    """
    if not reset_label or not on_reset:
        return False

    key_suffix = "reset_view" if mode == "view" else "reset_edit"
    if st.button(
        "",
        icon=":material/delete_forever:",
        type="secondary",
        help=reset_label,
        key=f"{namespace}:{key_suffix}",
        use_container_width=False,
    ):
        on_reset()
        return True
    return False

