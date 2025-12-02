from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.skills_evaluation.prompts.extract_reqs.examples import examples_reqs_extraction
from pipelines.skills_evaluation.prompts.extract_reqs.human import reqs_extraction_human_prompt as human
from pipelines.skills_evaluation.prompts.extract_reqs.system import system_reqs_prompt as system

# Оборачиваем системный промпт
system_prompt = SystemMessagePromptTemplate.from_template(system)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

examples = FewShotChatMessagePromptTemplate(
    examples=examples_reqs_extraction, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
extraction_reqs_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        examples,
        human_prompt,
    ]
)
