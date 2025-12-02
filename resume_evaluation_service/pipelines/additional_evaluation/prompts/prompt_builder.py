from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.additional_evaluation.prompts.examples import additional_info_examples
from pipelines.additional_evaluation.prompts.human import additional_info_human_prompt as human
from pipelines.additional_evaluation.prompts.system import system_additional_info_prompt as system

# Оборачиваем системный промпт
additional_system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

additional_examples = FewShotChatMessagePromptTemplate(
    examples=additional_info_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
additional_human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
additional_full_prompt = ChatPromptTemplate.from_messages(
    [
        additional_system_prompt,
        additional_examples,
        additional_human_prompt,
    ]
)
