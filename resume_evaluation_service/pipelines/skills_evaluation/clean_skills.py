"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс очистки скилов.
"""

from typing import Optional

from utils.logger import setup_logger
from pipelines.skills_evaluation.clean_skills_llm.clean_skills import clean_skills_llm
from pipelines.skills_evaluation.pydantic_models.clean_skills import SkillsList

# Логирование
logger = setup_logger(__name__)


async def get_cleaned_skills(skills: list) -> Optional[SkillsList]:
    """
    Асинхронно чистит скилы

    Args:
        text (str): Текст вакансии или резюме.

    Returns:
        Извлечённые данные или None при ошибке.
    """
    # Проверяем, что список скилов не пустой и не состоит только из пробелов
    if not skills or all(skill.strip() == '' for skill in skills):
        logger.warning("Пустой список для очистки скилов")
        return {'status': 'failed'}

    try:
        result = await clean_skills_llm(skills)
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}
        
        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        logger.info('Нормализация скилов завершена успешно')
        return result_dict
        
    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}
