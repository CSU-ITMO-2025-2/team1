# resume_evaluation_service/pipelines/education_evaluation/get_report.py
"""
Модуль для генерации полного отчёта по образованию и курсам.
Следует логике: оценка образования → оценка курсов → финальный балл до 20.
"""

from typing import Any, Dict, List, Optional, Set

from utils.logger import setup_logger
from pipelines.education_evaluation.pydantic_models.extract_courses import CourseList
from pipelines.education_evaluation.course_relevance import get_courses_relevance

# Логирование
logger = setup_logger(__name__)


def format_education_list(edu_list: list) -> Optional[list]:
    """Форматирует список образования для вывода."""
    if not edu_list:
        return None
    return [
        {"level": edu.get("level"), "specialization": edu.get("specialization")} for edu in edu_list
    ]


def format_course_list(course_list: dict) -> Optional[list]:
    """Форматирует список курсов для вывода."""
    if not course_list or not hasattr(course_list, "course_list"):
        return None
    return [
        {"course_name": course.get("course_name"), "description": course.get("description")}
        for course in course_list.get('course_list')
    ]


def get_report(
    resume_edu: dict,
    vacancy_edu: dict,
    resume_courses: dict,
    courses_relevance: dict
) -> dict:
    """
    Полная оценка соответствия кандидата по образованию и курсам.

    Args:
        resume_edu: Объект EsucationList — образование из резюме
        vacancy_edu: Объект EsucationList — требования из вакансии
        resume_courses: Курсы кандидата
        courses_relevance: Словарь соответствия курсов кандидата и вакансии

    Returns:
        Полный отчёт о сравнении образования и курсов кандидата с требованиями
        вакансии в формате, соответствующем бизнес-логике.
    """
    logger.info("Генерация полного отчёта по образованию и курсам")

    # Проверяем налицие всех обязательных аргументов
    if not all([resume_edu, vacancy_edu, resume_courses, courses_relevance]):
        logger.info("Не хватает обязательных аргументов")
        return {"status": 'failed'}

    vacancy = vacancy_edu.get('edu_list')
    resume = resume_edu.get('edu_list')

    # === 1. Проверка уровня образования ===
    # True - если требуется образование
    education_required = any(
        edu.get('level') in ["Высшее", "Среднее-специальное"] for edu in vacancy
    )

    # Если образование не требуется, выставляем максимальный балл
    if not education_required:
        education_level_score = 10
        education_specialization_score = 5
        education_level_comment = "В вакансии не указаны требования к уровню образования — выставлено 10 баллов"
        education_specialization_comment = "В вакансии не указаны требования к специализации — выставлено 5 баллов"
        min_required_level = "Не указано"
        required_specializations = {"Не указано"}
        required_levels = []
        candidate_levels = [] # todo вывести уровни кандидата даже если не требуется
        candidate_has_required_level = True
    else:
        # Собираем требуемые уровни и отбираем только высшее и среднее-специальное
        required_levels = [
            edu.get('level') for edu in vacancy if edu.get('level') in ["Высшее", "Среднее-специальное"]
        ]

        # Определяем минимальный требуемый уровень - если есть "Среднее-специальное", то это минимальный уровень
        if "Среднее-специальное" in required_levels:
            min_required_level = "Среднее-специальное"
        elif "Высшее" in required_levels:
            min_required_level = "Высшее"
        else:
            min_required_level = "Не указано"

        # Проверяем уровень кандидата. У кандидата может быть несколько уровней образования
        candidate_has_required_level = False
        candidate_levels = []

        for edu in resume:
            level = edu.get('level')
            candidate_levels.append(level)
            if level == "Не указано":
                continue
            # Если уровень совпадает с минимальным в вакансии, то подходит
            if level == min_required_level:
                candidate_has_required_level = True
            # Если уровень кандидата выше минимального, то подходит
            elif level == "Высшее" and min_required_level == "Среднее-специальное":
                candidate_has_required_level = True  # Высшее покрывает среднее

        if not candidate_has_required_level:
            # Если уровень кандидата ниже минимального, то ставим 0
            education_level_score = 0
            education_level_comment = f"Уровень/и образования кандидата ({candidate_levels}) не соответствует минимальному требованию вакансии ({min_required_level})"
        else:
            # Если уровень кандидата соответствует/выше минимального, то ставим 10
            education_level_score = 10
            education_level_comment = f"Уровень образования соответствует требованию ({min_required_level})"

    # Проверка специализации
    # Получаем области специализации вакансии и резюме
    vacancy_spec_set = {
        spec for edu in vacancy for spec in edu.get('specialization') if spec != "Не указано"
    }
    resume_spec_set = {
        spec for edu in resume for spec in edu.get('specialization') if spec != "Не указано"
    }

    required_specializations = vacancy_spec_set or {"Не указано"}

    # Если специализация не указана в вакансии, то ставим 5 баллов
    if not vacancy_spec_set or "Не указано" in vacancy_spec_set:
        education_specialization_score = 5
        education_specialization_comment = "Специализация не указана в вакансии — выставлено 5 баллов"
        common_specs = {}
    else:
        # Ищем пересечение специализаций вакансии и резюме
        common_specs = vacancy_spec_set & resume_spec_set
        if common_specs:
            education_specialization_score = 5
            education_specialization_comment = f"Найдено совпадение по специализации: {', '.join(common_specs)}"
        else:
            education_specialization_score = 0
            education_specialization_comment = f"Специализация не совпадает (вакансия: {list(vacancy_spec_set)}, резюме: {list(resume_spec_set)})"


    # === 2. ОЦЕНКА КУРСОВ ===
    if not resume_courses or not resume_courses.get('course_list'):
        education_courses_score = 0
        education_courses_comment = "У кандидата нет пройденных курсов"
    else:
        relevance_skills = courses_relevance.get("courses", []) if courses_relevance else []

        if not relevance_skills:
            education_courses_score = 0
            education_courses_comment = "Не удалось оценить релевантность курсов"
        elif any(item.get("relevance", False) for item in relevance_skills):
            relevant_count = sum(1 for item in relevance_skills if item.get("relevance"))
            education_courses_score = 5
            education_courses_comment = f"Кандидат прошёл {relevant_count} релевантных курса(ов) — добавлено 5 баллов"
        else:
            education_courses_score = 0
            education_courses_comment = "Ни один из курсов не соответствует требованиям вакансии"

    # Финальный балл
    final_score = education_level_score + education_specialization_score + education_courses_score

    # Релевантные и нерелевантные курсы
    relevant_courses = [item for item in courses_relevance.get("courses", []) if item.get("relevance")]
    irrelevant_courses = [item for item in courses_relevance.get("courses", []) if not item.get("relevance")]

    # === ИТОГОВЫЙ ОТЧЁТ ===
    final_evaluation = {
        "final_score": final_score,
        "education_level": {
            "max_score": 10,
            "education_level_score" : education_level_score,
            "education_level_comment": education_level_comment,
            "required_vacancy_level": min_required_level,
            "required_levels": required_levels,
            "candidate_levels": candidate_levels,
            "candidate_has_required_level": candidate_has_required_level,
        },
        "education_specialization": {
            "max_score": 5,
            "education_specialization_score": education_specialization_score,
            "education_specialization_comment": education_specialization_comment,
            "required_specializations": list(required_specializations),
            "candidate_specializations": list(resume_spec_set),
            "candidate_has_required_specialization": list(common_specs),
        },
        "education_courses": {
            "max_score": 5,
            "education_courses_score": education_courses_score,
            "education_courses_comment": education_courses_comment,
            "relevant_courses": relevant_courses,
            "irrelevant_courses": irrelevant_courses,
        },
        "status": "success"
    }

    logger.info("Отчёт сгенерирован: финальный балл = %d/20", final_score)
    return final_evaluation
