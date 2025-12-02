"""
Модуль для генерации отчёта по оценке релевантности и достаточности опыта работы кандидата.
"""

from datetime import date, datetime
from typing import Any, Dict, Optional

from dateutil.relativedelta import relativedelta

from utils.logger import setup_logger
from pipelines.work_exp_evaluation.pydantic_models.extract_work_exp import WorkExpList
from pipelines.work_exp_evaluation.pydantic_models.extract_work_reqs import WorkExpInfo as WorkExpReqInfo

# Логирование
logger = setup_logger(__name__)


def parse_date_safe(date_value) -> Optional[date]:
    """Парсит дату и возвращает объект date."""
    if isinstance(date_value, date):
        return date_value
    if isinstance(date_value, str):
        try:
            # Ожидаем формат YYYY-MM-DD
            return datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Не удалось распарсить дату: {date_value}")
            return None
    return None


def parse_duration_safe(duration_str: str) -> Optional[int]:
    """Парсит строку длительности и возвращает количество месяцев."""
    if not duration_str:
        return None
    try:
        years = 0
        months = 0
        parts = duration_str.split()
        i = 0
        while i < len(parts):
            if parts[i].isdigit():
                val = int(parts[i])
                if i + 1 < len(parts):
                    unit = parts[i + 1].lower().replace(",", "").replace(".", "")
                    if unit in ["год", "года", "лет", "г", "г."]:
                        years += val
                        i += 2
                        continue
                    elif unit in ["мес", "месяц", "месяца", "месяцев", "м", "м."]:
                        months += val
                        i += 2
                        continue
            i += 1
        total_months = years * 12 + months
        return total_months if total_months > 0 else None
    except Exception as e:
        logger.warning(f"Ошибка при парсинге длительности '{duration_str}': {e}")
        return None


def evaluate_work_experience_match(
    resume_work_exp: dict,
    vacancy_required_exp: dict,
    relevance_result: dict,
) -> dict:
    """
    Генерирует полный отчёт по опыту работы кандидата.

    Args:
        resume_work_exp: Pydantic-модель с опытом работы из резюме.
        vacancy_required_exp: Pydantic-модель с требуемым опытом из вакансии.
        relevance_result: Результат оценки релевантности
    Returns:
        Словарь с полным отчётом по опыту работы кандидата.
    """
    logger.info("Генерация отчёта по опыту работы")

    # --- 1. Подготовка данных ---
    work_list_data = resume_work_exp.get('work_list') if resume_work_exp else []
    relevance_exp_data = relevance_result.get('pairs') if relevance_result else []
    required_years = int(vacancy_required_exp.get('work_years')) if vacancy_required_exp else 0
    required_months = required_years * 12 if required_years is not None else 0

    # --- 2. Добавление релевантности в список опыта ---
    # Создаем словарь для сопоставления релевантности с опытом работы
    relevance_dict = {}
    if relevance_exp_data:
        for pair in relevance_exp_data:
            relevance_dict[pair.get('company_position')] = {
                "relevance": pair.get('relevance'),
                "reason": pair.get('reason'),
            }

    # Обогащаем список опыта данными о релевантности
    work_list = []
    for job in work_list_data:
        key = f"{job['company_name']} | {job['position']}"
        relevance_info = relevance_dict.get(
            key, {"relevance": None, "reason": "Не оценено"}
        )
        job["relevance"] = relevance_info["relevance"]
        job["reason"] = relevance_info["reason"]
        work_list.append(job)

    # --- 3. Добавляем нужные даты и обработаем длительность опыта работы, cчитаем частую смену работы ---

    # Текущая дата и дата за год назад
    today = date.today()
    one_year_ago = today - relativedelta(years=1)

    # Список работ начатых и законченных за последний год
    recent_jobs_list = []

    # Счетчик работ начатых и законченных за последний год
    recent_jobs_count = 0

    for job in work_list:
        # Случай, когда есть обе даты начала и окончания (прошлая работа)
        if job.get("start_date") and job.get("end_date"):
            start_date = parse_date_safe(job.get("start_date"))
            end_date = parse_date_safe(job.get("end_date"))
            duration_months = parse_duration_safe(job.get('duration'))
            delta = relativedelta(end_date, start_date)
            calculated_duration_months = delta.years * 12 + delta.months
            job["calculated_duration_months"] = calculated_duration_months
            job["calculated_duration_str"] = f"{delta.years} г. {delta.months} мес."
            job["has_duration"] = True
            job["duration_difference"] = True if calculated_duration_months != duration_months else False
            job["true_duration"] = duration_months if calculated_duration_months <= duration_months else calculated_duration_months
            job["true_duration_str"] = f"{delta.years} г. {delta.months} мес." if calculated_duration_months >= duration_months else f"{duration_months // 12} г. {duration_months % 12} мес."

            # Проверка на частую смену работы (за последний год)
            if start_date >= one_year_ago and end_date >= one_year_ago:
                recent_jobs_count += 1
                recent_jobs_list.append(job)

            # Случай, когда есть только дата начала и нет даты окончания (текущая работа)
        elif job.get("start_date") and not job.get("end_date"):
            start_date = parse_date_safe(job.get("start_date"))
            delta = relativedelta(today, start_date)
            calculated_duration_months = delta.years * 12 + delta.months
            job["calculated_duration_months"] = calculated_duration_months
            job["calculated_duration_str"] = f"{delta.years} г. {delta.months} мес."
            job["has_duration"] = True
            job["duration_difference"] = False
            job["true_duration"] = calculated_duration_months
            job["true_duration_str"] = f"{delta.years} г. {delta.months} мес."

            # В остальных случаях мы не определим длительность работы
        else:
            job["calculated_duration_months"] = 0
            job["calculated_duration_str"] = "Невозможно определить длительность работы"
            job["has_duration"] = False
            job["duration_difference"] = False
            job["true_duration"] = 0
            job["true_duration_str"] = "Невозможно определить длительность работы"



    # --- 4. Посчитаем опыт работы ---

    # Общий опыт работы
    total_work_exp_months = sum((job.get("true_duration") or 0) for job in work_list)

    # Приводим  к виду "X лет Y месяцев"
    total_work_exp_str= f"{total_work_exp_months // 12} г. {total_work_exp_months % 12} мес."


    # Преобразуем даты в строки для каждой работы
    for job in work_list:
        if job.get('start_date') and hasattr(job['start_date'], 'strftime'):
            job['start_date'] = job['start_date'].strftime('%Y-%m-%d')
        if job.get('end_date') and hasattr(job['end_date'], 'strftime'):
            job['end_date'] = job['end_date'].strftime('%Y-%m-%d')

    # Релевантный опыт
    total_relevant_work_exp_months = sum(
        (job.get("true_duration") or 0)
        for job in work_list
        if job.get("relevance") is True
    )
    total_relevant_work_exp_str= f"{total_relevant_work_exp_months // 12} г. {total_relevant_work_exp_months % 12} мес."

    relevant_work_exp_list = [job for job in work_list if job.get("relevance") is True]

    # Нерелевантный опыт
    total_irrelevant_work_exp_months = sum(
        (job.get("true_duration") or 0)
        for job in work_list
        if job.get("relevance") is False
    )

    total_irrelevant_work_exp_str= f"{total_irrelevant_work_exp_months // 12} г. {total_irrelevant_work_exp_months % 12} мес."
    irrelevant_work_exp_list = [job for job in work_list if job.get("relevance") is False]


    # --- 5. Оценка соответствия требуемому опыту ---


    # Максимальный балл за блок опыта работы без проверки частоты смены работы
    max_score = 30

    if total_relevant_work_exp_months == 0 and total_relevant_work_exp_months > 0:
        # Если опыт не требуется, ставим максимальный балл
        score_comment = "На данную вакансию не требуется опыт - выставлено 30 баллов"
        score = max_score
    elif total_relevant_work_exp_months == 0:
        score_comment = "У кандидата нет релевантного опыта - выставлено 0 баллов"
        score = 0
    elif total_relevant_work_exp_months >= required_months:
        score_comment = "Опыт кандидата выше или равен требуемому - выставлено 30 баллов"
        score = max_score
    elif total_relevant_work_exp_months >= required_months - 6:
        score_comment = "Опыт кандидата меньше на полгода - выставлено 25 баллов"
        score = 25
    elif total_relevant_work_exp_months >= required_months - 12:
        score_comment = "Опыт кандидата меньше на год - выставлено 15 баллов"
        score = 15
    elif total_relevant_work_exp_months >= required_months - 24:
        score_comment = "Опыт кандидата меньше на 2 года - выставлено 10 баллов"
        score = 10
    elif total_relevant_work_exp_months >= required_months - 36:
        score_comment = "Опыт кандидата меньше на 3 года - выставлено 5 баллов"
        score = 5
    else:
        score_comment = "Опыт кандидата меньше на 3 и более года - выставлено 0 баллов"
        score = 0


    # --- 6. Проверка стабильности занятости ---

    # Максимальное количество баллов за стабильность занятости
    job_change_max_score = 5

    job_change_flag = recent_jobs_count >= 2
    job_change_score = job_change_max_score if job_change_flag is False else 0
    job_change_reason = (
        f"Кандидат сменил {recent_jobs_count} места работы за последний год ({one_year_ago} - {today})"
        if job_change_flag
        else "Частая смена работы не выявлена у кандидата"
    )

    # Период проверки стабильности занятости
    job_change_check_period = f"{one_year_ago.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}"


    # --- 7. Формирование финального отчёта ---

    # Расчет финальной оценки
    final_score = score + job_change_score

    final_max_score = max_score + job_change_max_score

    final_result = {
        'status': "success",
        'max_score': final_max_score,
        'final_score': final_score,
        'job_change_data': {
            'job_change_flag': job_change_flag,
            'job_change_reason': job_change_reason,
            'job_change_score': job_change_score,
            'job_change_score_max_score': job_change_max_score,
            'job_change_check_period': job_change_check_period,
        },
        'work_exp_data': {
            'work_exp_score': score,
            'work_exp_comment': score_comment,
            'work_exp_max_score': max_score,
            'total_work_exp_months': total_work_exp_months,
            'total_work_exp': total_work_exp_str,
            'total_relevant_work_exp_months': total_relevant_work_exp_months,
            'total_relevant_work_exp': total_relevant_work_exp_str,
            'relevant_work_exp_list': relevant_work_exp_list,
            'total_irrelevant_work_exp_months': total_irrelevant_work_exp_months,
            'total_irrelevant_work_exp': total_irrelevant_work_exp_str,
            'irrelevant_work_exp_list': irrelevant_work_exp_list,
        },
        'required_exp_years': required_years,
    }

    logger.info(
        f"Отчёт по опыту работы сгенерирован. Финальный балл: {final_score}/{final_max_score}"
    )
    return final_result
