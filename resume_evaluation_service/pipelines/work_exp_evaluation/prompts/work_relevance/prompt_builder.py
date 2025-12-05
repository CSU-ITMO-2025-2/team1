from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.work_exp_evaluation.prompts.work_relevance.examples import work_experience_relevance_examples
from pipelines.work_exp_evaluation.prompts.work_relevance.human import work_relevance_human_prompt as human
from pipelines.work_exp_evaluation.prompts.work_relevance.system import work_experience_relevance_system_prompt as system

# Оборачиваем системный промпт
work_relevance_system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

work_relevance_examples = FewShotChatMessagePromptTemplate(
    examples=work_experience_relevance_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
work_relevance_human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
work_relevance_full_prompt = ChatPromptTemplate.from_messages(
    [
        work_relevance_system_prompt,
        work_relevance_examples,
        work_relevance_human_prompt,
    ]
)
