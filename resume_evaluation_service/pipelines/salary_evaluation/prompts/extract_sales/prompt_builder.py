from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from .examples import salary_extraction_examples as examples_list
from .human_prompt import salary_extraction_human_prompt as human
from .system_prompt import system_salary_extraction_prompt as system

# Оборачиваем системный промпт
salary_extraction_system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

salary_extraction_examples = FewShotChatMessagePromptTemplate(
    examples=examples_list, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
salary_extraction_human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
salary_extraction_full_prompt = ChatPromptTemplate.from_messages(
    [
        salary_extraction_system_prompt,
        salary_extraction_examples,
        salary_extraction_human_prompt,
    ]
)
