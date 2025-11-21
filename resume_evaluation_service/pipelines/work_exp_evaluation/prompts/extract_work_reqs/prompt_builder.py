from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from .examples import work_years_extraction_examples
from .human import work_requirements_human_prompt as human
from .system import system_extract_work_years_prompt as system

# Оборачиваем системный промпт
work_years_reqs_system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

work_years_reqs_examples = FewShotChatMessagePromptTemplate(
    examples=work_years_extraction_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
work_years_reqs_human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
work_years_full_prompt = ChatPromptTemplate.from_messages(
    [
        work_years_reqs_system_prompt,
        work_years_reqs_examples,
        work_years_reqs_human_prompt,
    ]
)
