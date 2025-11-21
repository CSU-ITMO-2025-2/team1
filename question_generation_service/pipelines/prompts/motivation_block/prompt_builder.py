from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from .examples import motivation_block_examples as examples
from .human import human_motivation_block_prompt as human
from .system import motivation_block_system_prompt as system

# Оборачиваем системный промпт
system_prompt = SystemMessagePromptTemplate.from_template(system)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

# Оформляем примеры
prepared_examples = FewShotChatMessagePromptTemplate(
    examples=examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
motivaion_block_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        prepared_examples,
        human_prompt,
    ]
)
