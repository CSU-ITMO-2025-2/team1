from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from pipelines.work_exp_evaluation.prompts.extract_work_exp.examples import work_experience_examples
from pipelines.work_exp_evaluation.prompts.extract_work_exp.human import work_experience_human_prompt as human
from pipelines.work_exp_evaluation.prompts.extract_work_exp.system import system_work_experience_prompt as system

# Оборачиваем системный промпт
work_experience_system_prompt = SystemMessagePromptTemplate.from_template(
    system
)

# Оборачиваем примеры
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

work_exp_examples = FewShotChatMessagePromptTemplate(
    examples=work_experience_examples, example_prompt=example_prompt
)

# оборачиваем хьюман промпт
work_experience_human_prompt = HumanMessagePromptTemplate.from_template(human)

# Собираем промпт в шаблон
work_experience_full_prompt = ChatPromptTemplate.from_messages(
    [
        work_experience_system_prompt,
        work_exp_examples,
        work_experience_human_prompt,
    ]
)
