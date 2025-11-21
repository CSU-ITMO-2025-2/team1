"""
Модуль для генерации отчёта по оценке соответствия навыков кандидата требованиям вакансии.
"""

import logging
from typing import Any, Dict
from collections import defaultdict

# Настройка логирования
logger = logging.getLogger(__name__)


def get_report(
    resume_skills_data: dict,
    vacancy_skills_data: dict,
    aggregated_vacancy_skills: dict,
    name_to_category: dict,
    current_match: list,
    current_unmatched_skills: list,
    unmatched_vacancy_skills_relevance: dict
) -> Dict[str, Any]:
    """
    Генерирует полный отчёт по соответствию навыков кандидата требованиям вакансии.

    Args:
        resume_skills_data: Данные из резюме (dict).
        vacancy_skills_data: Данные из вакансии (dict).
        aggregated_vacancy_skills: Агрегированные навыки из вакансии (dict).
        name_to_category: Словарь для преобразования названий навыков в категории (dict).
        current_match: Текущий список совпадений (list).
        current_unmatched_skills: Текущий список несовпадений (list).
        unmatched_vacancy_skills_relevance: Результат оценки релевантности (dict).

    Returns:
        Словарь с полным отчётом.
    """
    logger.info("Генерация отчёта по соответствию навыков")


    # --- 1. Подготовка данных ---
    # must_have навыки
    must_have_skills_list = []

    for skill in vacancy_skills_data['must_have_skills']:
        if skill in name_to_category:
            must_have_skills_list.append(name_to_category[skill])

    must_have_skills = set(must_have_skills_list)

    # nice_to_have навыки
    nice_to_have_skills_list = []

    for skill in vacancy_skills_data['nice_to_have_skills']:
        if skill in name_to_category:
            nice_to_have_skills_list.append(name_to_category[skill])

    nice_to_have_skills = set(nice_to_have_skills_list)

    # Удаление навыков, которые уже есть в must_have из nice_to_have
    skills_to_remove = must_have_skills.intersection(nice_to_have_skills)

    for skill in skills_to_remove:
        nice_to_have_skills.remove(skill)

    must_have_skills = list(must_have_skills)
    nice_to_have_skills = list(nice_to_have_skills)


    # --- 2. Соберем словарь с навыками и релевантностью

    # нормализация и индексация
    norm = lambda s: s.strip().lower()
    current_set = {norm(s) for s in current_match}

    idx = defaultdict(list)
    for p in unmatched_vacancy_skills_relevance.get("pairs", []):
        vs = norm(p.get("vacancy_skill", ""))
        idx[vs].append(p)

    result = {"must_have_skills": {}, "nice_to_have_skills": {}}

    for group_name, skills in (
        ("must_have_skills", must_have_skills),
        ("nice_to_have_skills", nice_to_have_skills),
    ):
        for skill in sorted(skills, key=str.lower):
            s = norm(skill)

            # 1) Прямое совпадение с резюме
            if s in current_set:
                result[group_name][skill] = {
                    "relevance": "current",
                    "relevant_skill": skill,  # оставить как в вакансии
                    "reason": "Прямое совпадение термина.",
                }
                continue

            # 2) Поиск по таблице релевантности (full > half > none)
            pairs = idx.get(s, [])

            full = next((p for p in pairs if p.get("relevance") == "Полная аналогичность"), None)
            if full:
                result[group_name][skill] = {
                    "relevance": "current",
                    "relevant_skill": full.get("resume_skill"),  # можно поменять на skill, если нужно
                    "reason": full.get("reason") or "Полная аналогичность",
                }
                continue

            half = next((p for p in pairs if p.get("relevance") == "Частичная аналогичность"), None)
            if half:
                result[group_name][skill] = {
                    "relevance": "half",
                    "relevant_skill": half.get("resume_skill"),
                    "reason": half.get("reason") or "Частичная аналогичность",
                }
                continue

            # 3) Совпадений нет
            result[group_name][skill] = {
                "relevance": "no_relevance",
                "relevant_skill": None,
                "reason": "Совпадений не найдено.",
            }



    # --- 3. Формирование финального отчёта ---

    # Статистика
    # --- must_have ---

    mh_total = 0
    mh_current = 0
    mh_half = 0
    mh_relevant = 0
    mh_no_rel = 0
    mh_pct = 0.0

    if must_have_skills:
        mh = result.get("must_have_skills", {})
        mh_total = len(mh)
        mh_current = sum(1 for v in mh.values() if v.get("relevance") == "current")
        mh_half    = sum(1 for v in mh.values() if v.get("relevance") == "half")
        mh_relevant = mh_current + mh_half
        mh_no_rel   = mh_total - mh_relevant
        mh_pct = round((mh_relevant / mh_total * 100) if mh_total else 0.0, 1)

    # --- nice_to_have ---

    nh_total = 0
    nh_current = 0
    nh_half = 0
    nh_relevant = 0
    nh_no_rel = 0
    nh_pct = 0.0

    if nice_to_have_skills:
        nh = result.get("nice_to_have_skills", {})
        nh_total = len(nh)
        nh_current = sum(1 for v in nh.values() if v.get("relevance") == "current")
        nh_half    = sum(1 for v in nh.values() if v.get("relevance") == "half")
        nh_relevant = nh_current + nh_half
        nh_no_rel   = nh_total - nh_relevant
        nh_pct = round((nh_relevant / nh_total * 100) if nh_total else 0.0, 1)


    # Рассчитываем оценку

    max_score = 35

    mh_max_score = 20
    nh_max_score = 15

    if must_have_skills and not nice_to_have_skills:
        score = mh_pct / 100 * max_score
    elif not must_have_skills and nice_to_have_skills:
        score = nh_pct / 100 * max_score
    elif must_have_skills and nice_to_have_skills:
        score = mh_pct / 100 * mh_max_score + nh_pct / 100 * nh_max_score
    else:
        score = 0



    final_result = {
        'status': 'success',
        'max_score': max_score,
        'score': score,
        'skills_data': result,
        "must_have_stats": {
                "total_skills": mh_total,
                "relevant_count": mh_relevant,
                "current_count": mh_current,
                "half_count": mh_half,
                "no_relevance_count": mh_no_rel,
                "relevant_percentage": mh_pct,
            },
        "nice_to_have_stats": {
            "total_skills": nh_total,
            "relevant_count": nh_relevant,
            "current_count": nh_current,
            "half_count": nh_half,
            "no_relevance_count": nh_no_rel,
            "relevant_percentage": nh_pct,
        },
    }

    logger.info(
        f"Отчёт по навыкам сгенерирован. Балл: {score}/{max_score}"
    )
    return final_result
