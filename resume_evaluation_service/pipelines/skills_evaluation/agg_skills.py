"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс аггрегации навыков.
"""

from typing import Optional

from utils.logger import setup_logger
from pipelines.skills_evaluation.agg_skills_llm.agg_skills import agg_skills_llm
from pipelines.skills_evaluation.pydantic_models.agg_skills import AggregatedSkills

# Логирование
logger = setup_logger(__name__)


async def get_agg_skills(skills: list) -> Optional[AggregatedSkills]:
    """
    Асинхронно агрегирует навыки

    Args:
        skills (list): Список навыков

    Returns:
        Извлечённые данные или None при ошибке.
    """
    
    # Проверяем, что список скилов не пустой и не состоит только из пробелов
    if not skills or all(skill.strip() == '' for skill in skills):
        logger.warning("Пустой список для очистки скилов")
        return {'status': 'failed'}

    try:
        result = await agg_skills_llm(skills)
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}
        
        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        logger.info("Стандартизация навыков успешно выполнена")
        return result_dict
        
    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}
