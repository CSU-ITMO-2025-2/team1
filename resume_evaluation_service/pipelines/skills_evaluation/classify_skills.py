"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс классификации скилов.
"""

from typing import Optional

from utils.clean_text import clean_text
from utils.logger import setup_logger
from pipelines.skills_evaluation.classify_skills_llm.classify_skills import classify_skills_llm
from pipelines.skills_evaluation.pydantic_models.classify_skills import ParsedJobSkills

# Логирование
logger = setup_logger(__name__)


async def get_classify_reqs(vacancy_requirements: str) -> Optional[ParsedJobSkills]:
    """
    Асинхронно классифицирует требования вакансии

    Args:
        vacancy_requirements (str): блок требований в вакансии

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем, что текст не пустой и не состоит только из пробелов
    if not vacancy_requirements or not vacancy_requirements.strip():
        logger.warning("Пустой текст для извлечения опыта работы")
        return {'status': 'failed'}

    # очищаем текст
    logger.info("Очищаем текст от лишних символов")
    cleaned_vacancy_requirements = clean_text(vacancy_requirements)

    try:
        result = await classify_skills_llm(cleaned_vacancy_requirements)
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}
        
        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        logger.info("Классификация навыков  прошла успешно")
        return result_dict
        
    except Exception as e:
        logger.error("Ошибка выполнения: %s", str(e), exc_info=True)
        return {'status': 'failed'}
