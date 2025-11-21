from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from .examples import parsing_examples
from .human_prompt import parsing_human_prompt as human
from .system_prompt import system_parsing_prompt

# Оборачиваем системный промпт
system_prompt = SystemMessagePromptTemplate.from_template(system_parsing_prompt)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

# Оформляем примеры
examples = FewShotChatMessagePromptTemplate(
    examples=parsing_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
parsing_full_prompt = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        examples,
        human_prompt,
    ]
)
