from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.education_evaluation.prompts.extract_main_edu.extract_main_edu_examples import education_examples
from pipelines.education_evaluation.prompts.extract_main_edu.extract_main_edu_human import education_human_prompt as human
from pipelines.education_evaluation.prompts.extract_main_edu.extract_main_edu_system import system_education_prompt as system

# Оборачиваем системный промпт
extract_main_edu_system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

extract_main_edu_examples = FewShotChatMessagePromptTemplate(
    examples=education_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
extract_main_edu_human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
extract_main_edu_full_prompt = ChatPromptTemplate.from_messages(
    [
        extract_main_edu_system_prompt,
        extract_main_edu_examples,
        extract_main_edu_human_prompt,
    ]
)
