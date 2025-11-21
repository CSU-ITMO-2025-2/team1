"""Компонент кнопки копирования."""

import uuid

import streamlit.components.v1 as components


def copy_icon(
    text: str,
    *,
    key: str,
    tooltip: str = "Копировать",
    label: str = "",
    icon_variant: str = "material_symbols",  # noqa: ARG001
) -> None:
    """Отображает кнопку копирования текста в буфер обмена.

    Использует JavaScript API для копирования текста в буфер обмена.

    Args:
        text: Текст для копирования
        key: Уникальный ключ для кнопки
        tooltip: Подсказка при наведении
        label: Текст кнопки
        icon_variant: Вариант иконки (не используется, для совместимости)

    """
    # Генерируем уникальный ID для этой кнопки
    unique_id = f"copy_btn_{uuid.uuid4().hex[:8]}"

    # HTML с кнопкой и JavaScript для копирования
    html_code = f"""
    <div style="display: inline-block;">
        <button
            id="{unique_id}"
            title="{tooltip}"
            style="
                border-radius: 10px;
                border: 1px solid rgba(15,23,42,.2);
                background: rgba(15,23,42,.03);
                color: #0f172a;
                padding: 0;
                min-height: 40px;
                height: 40px;
                min-width: 40px;
                width: 40px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 20px;
                transition: all 0.15s ease;
            "
            onmouseover="this.style.background='rgba(15,23,42,.08)'"
            onmouseout="this.style.background='rgba(15,23,42,.03)'"
            onmousedown="this.style.background='rgba(15,23,42,.15)'"
            onmouseup="this.style.background='rgba(15,23,42,.08)'"
        >
            <svg xmlns="http://www.w3.org/2000/svg" height="24"
                viewBox="0 -960 960 960" width="24" fill="currentColor">
                <path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0
                    56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33
                    0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/>
            </svg>
        </button>
        <script>
            (function() {{
                const button = document.getElementById('{unique_id}');
                const originalSVG = button.innerHTML;
                const checkSVG = '<svg xmlns="http://www.w3.org/2000/svg" height="24"' +
                    ' viewBox="0 -960 960 960" width="24" fill="currentColor">' +
                    '<path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z"/></svg>';

                button.addEventListener('click', function() {{
                    const text = {text!r};
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        navigator.clipboard.writeText(text).then(function() {{
                            // Визуальная отдача - меняем иконку на галочку
                            button.innerHTML = checkSVG;
                            button.style.background = 'rgba(16,185,129,.15)';
                            button.style.borderColor = 'rgba(16,185,129,.4)';
                            button.style.color = 'rgb(16,185,129)';

                            // Возвращаем исходную иконку через 2 секунды
                            setTimeout(function() {{
                                button.innerHTML = originalSVG;
                                button.style.background = 'rgba(15,23,42,.03)';
                                button.style.borderColor = 'rgba(15,23,42,.2)';
                                button.style.color = '#0f172a';
                            }}, 2000);
                        }}).catch(function(err) {{
                            console.error('Ошибка при копировании: ', err);
                        }});
                    }} else {{
                        // Fallback для старых браузеров
                        const textarea = document.createElement('textarea');
                        textarea.value = text;
                        textarea.style.position = 'fixed';
                        textarea.style.opacity = '0';
                        document.body.appendChild(textarea);
                        textarea.select();
                        try {{
                            document.execCommand('copy');
                            // Визуальная отдача
                            button.innerHTML = checkSVG;
                            button.style.background = 'rgba(16,185,129,.15)';
                            setTimeout(function() {{
                                button.innerHTML = originalSVG;
                                button.style.background = 'rgba(15,23,42,.03)';
                            }}, 2000);
                        }} catch (err) {{
                            console.error('Ошибка при копировании (fallback): ', err);
                        }}
                        document.body.removeChild(textarea);
                    }}
                }});
            }})();
        </script>
    </div>
    """

    components.html(html_code, height=50, scrolling=False)
