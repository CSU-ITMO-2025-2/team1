"""Функции для экспорта контента в PDF."""

import os
import re
import textwrap
from pathlib import Path
from functools import cache

import fitz

# Константы для PDF
A4_WIDTH, A4_HEIGHT = fitz.paper_size("a4")
PAGE_MARGIN_X = 70
PAGE_MARGIN_Y = 80
LINE_HEIGHT = 16
TITLE_FONT_SIZE = 16
BODY_FONT_SIZE = 11
PDF_ICON = ":material/picture_as_pdf:"
ENV_PDF_FONT = "HR_ASSIST_PDF_FONT"
WATERMARK_TEXT = "HR-Assistant"


@cache
def get_pdf_font() -> fitz.Font:
    """Ленивая загрузка шрифта с поддержкой кириллицы."""
    env_font = os.environ.get(ENV_PDF_FONT)
    if env_font:
        font_path = Path(env_font).expanduser()
        if font_path.exists():
            return fitz.Font(fontfile=str(font_path))

    # Попробуем стандартные системные шрифты с поддержкой кириллицы
    fallback_fonts = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    ]

    for font_path in fallback_fonts:
        if font_path.exists():
            return fitz.Font(fontfile=str(font_path))

    return fitz.Font("helv")


def normalize_md(text: str) -> str:
    """Очищает markdown и нормализует переносы строк."""
    s = text.replace("\r\n", "\n").replace("\r", "\n")
    s = textwrap.dedent(s)
    s = re.sub(r"^[ \t]{4,}", "", s, flags=re.MULTILINE)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    return s.strip()


def markdown_to_plain_lines(md_text: str, *, wrap: int = 88) -> list[str]:
    """Преобразует markdown текст в список простых строк для PDF."""
    text = normalize_md(md_text)
    # Убираем основные элементы Markdown, чтобы в PDF был "чистый" текст.
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1 (\2)", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = text.replace("\t", "    ")

    lines: list[str] = []
    for paragraph in text.splitlines():
        if not paragraph.strip():
            lines.append("")
            continue
        wrapped = textwrap.wrap(paragraph, width=wrap, break_long_words=False, replace_whitespace=False)
        lines.extend(wrapped or [""])
    return lines


def build_pdf_bytes(case_input: str, sections: list[tuple[str, str]], title: str = "Заявка на подбор") -> bytes:
    """Формирует PDF с вводными данными и несколькими секциями.
    
    Args:
        case_input: Исходные данные для заявки
        sections: Список секций с заголовками и текстом
        title: Главный заголовок документа (по умолчанию "Заявка на подбор")
    
    """
    doc = fitz.open()
    font = get_pdf_font()

    def new_page() -> tuple[fitz.Page, fitz.TextWriter, float]:
        page = doc.new_page(width=A4_WIDTH, height=A4_HEIGHT)
        writer = fitz.TextWriter(page.rect)
        return page, writer, PAGE_MARGIN_Y

    def flush(current_page: fitz.Page, current_writer: fitz.TextWriter) -> None:
        current_writer.write_text(current_page)
        current_page.insert_text(
            (A4_WIDTH - 150, 30),
            WATERMARK_TEXT,
            fontsize=10,
            fontname="helv",
            color=(0.0196, 0.3137, 0.6274),
        )

    page, writer, y = new_page()

    def ensure_space(lines_count: float = 1.0) -> None:
        nonlocal page, writer, y
        required = LINE_HEIGHT * lines_count
        if y + required > (A4_HEIGHT - PAGE_MARGIN_Y):
            flush(page, writer)
            page, writer, y = new_page()

    def write_heading(
        text: str,
        size: int = TITLE_FONT_SIZE,
        *,
        top_gap: float = 1.0,
        bottom_gap: float = 1.5,
    ) -> None:
        nonlocal y
        if not text:
            return
        ensure_space(top_gap)
        y += LINE_HEIGHT * top_gap
        writer.append((PAGE_MARGIN_X, y), text, font=font, fontsize=size)
        y += LINE_HEIGHT * bottom_gap

    def write_lines(lines: list[str]) -> None:
        nonlocal y, page, writer
        for line in lines or [""]:
            ensure_space(1.0)
            writer.append(
                (PAGE_MARGIN_X, y),
                line if line else " ",
                font=font,
                fontsize=BODY_FONT_SIZE,
            )
            y += LINE_HEIGHT
        y += LINE_HEIGHT * 0.5

    write_heading(title, TITLE_FONT_SIZE + 6, top_gap=2.0, bottom_gap=2.2)

    if case_input and case_input.strip():
        write_heading("Исходные данные", TITLE_FONT_SIZE + 2, top_gap=1.5, bottom_gap=1.8)
        write_lines(markdown_to_plain_lines(case_input))

    for section_title, section_text in sections:
        lines = markdown_to_plain_lines(section_text)
        if not any(line.strip() for line in lines):
            continue
        write_heading(section_title, TITLE_FONT_SIZE + 2, top_gap=1.2, bottom_gap=1.6)
        write_lines(lines)

    flush(page, writer)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def pdf_file_name(label: str) -> str:
    """Генерирует имя файла для PDF из метки."""
    clean = re.sub(r"\s+", "_", label.strip())
    return f"{clean or 'export'}.pdf"

