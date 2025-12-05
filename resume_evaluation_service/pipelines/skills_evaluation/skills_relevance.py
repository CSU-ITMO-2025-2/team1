"""
Функция-обертка, которая обрабатывает входной текст и запускает процесс оценки релевантности скиллов
"""

from utils.logger import setup_logger
from pipelines.skills_evaluation.skills_relevance_llm.skills_relevance import skills_relevance_llm

# Логирование
logger = setup_logger(__name__)


async def get_skills_relevance(
    unmatched_vac_list: list, unmatched_res_list: list, pairs
):
    """
    Асинхронно оценивает редевантность

    Args:
        unmatched_vac_list (list): список нерелевантных скилов в вакансии
        unmatched_res_list (list): список нерелевантных скилов в резюме
        pairs (list): список пар скилов для сравнения

    Returns:
        Извлечённые данные или None при ошибке.
    """
    
    # Проверяем, что список скилов не пустой и не состоит только из пробелов
    if not unmatched_vac_list or all(skill.strip() == '' for skill in unmatched_vac_list):
        logger.warning("Пустой список для очистки скилов")
        return {'status': 'failed'}
    
    # Проверяем, что список скилов не пустой и не состоит только из пробелов
    if not unmatched_res_list or all(skill.strip() == '' for skill in unmatched_res_list):
        logger.warning("Пустой список для очистки скилов")
        return {'status': 'failed'}
        
    # # Проверяем, что список скилов не пустой и не состоит только из пробелов
    # if not pairs or all(skill.strip() == '' for skill in pairs):
    #     logger.warning("Пустой список для очистки скилов")
    #     return {'status': 'failed'}

    try:
        result = await skills_relevance_llm(
            unmatched_vac_list, unmatched_res_list, pairs
        )
        # Проверяем, что результат не None
        if result is None:
            logger.error("Результат равен None")
            return {'status': 'failed'}
        
        # Переводим в словарь
        result_dict = result.model_dump()

        # Устанавливаем флаг успешного выполнения
        result_dict['status'] = 'success'
        logger.info("Оценка релевантности навыков выполнена успешно")
        return result_dict
        
    except Exception as e:
        logger.error(f"Ошибка выполнения: {str(e)}", exc_info=True)
        return {'status': 'failed'}
