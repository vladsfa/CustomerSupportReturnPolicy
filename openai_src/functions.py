import concurrent.futures
from openai_src.native_assistant import client
from openai_src.constants import QUESITON_DECOMPOSITOR_MODEL, QUESITON_DECOMPOSITOR_TEMPERATURE
from openai_src.constants import QUESITON_DECOMPOSITOR_INSTRUCTIONS, QUESTION_DECOMPOSITOR_SCHEMA

from openai_src.constants import INFO_RETRIEVER_MODEL, INFO_RETRIEVER_INSTRUCTIONS, INFO_RETRIEVER_TEMPERATURE

from openai_src.constants import ANSWER_BUILDER_MODEL, ANSWER_BUILDER_INSTRUCTIONS, ANSWER_BUILDER_TEMPERATURE, ANSWER_BUILDER_MESSAGE_BUILD

import json

from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent

def parse_questions(complex_question):
    simpler_questions = client.beta.chat.completions.parse(
        model=QUESITON_DECOMPOSITOR_MODEL,
        temperature=QUESITON_DECOMPOSITOR_TEMPERATURE,
        messages=[
            {"role": "system", "content": QUESITON_DECOMPOSITOR_INSTRUCTIONS},
            {"role": "user", "content": complex_question}
        ],
        response_format={"type": "json_schema", "json_schema": QUESTION_DECOMPOSITOR_SCHEMA}
    )
    return json.loads(simpler_questions.choices[0].message.content)['simpler_questions']


def process_simpler_question(question):
    question_answer = client.chat.completions.create(
        model=INFO_RETRIEVER_MODEL,
        temperature=INFO_RETRIEVER_TEMPERATURE,
        messages=[
            {"role": "system", "content": INFO_RETRIEVER_INSTRUCTIONS},
            {"role": "user", "content": question}
        ]
    ).choices[0].message.content

    return question, question_answer

def get_simpler_questions_answer(simpler_questions):
    result = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for question in simpler_questions:
            futures.append(executor.submit(process_simpler_question, question))
        
        for future in concurrent.futures.as_completed(futures):
            q, answer = future.result()
            result.append(answer)
    return result

def get_question_answer(message):
    simpler_questions = parse_questions(message)

    answers = get_simpler_questions_answer(simpler_questions)

    main_answer = client.chat.completions.create(
        model=ANSWER_BUILDER_MODEL,
        temperature=ANSWER_BUILDER_TEMPERATURE,
        messages=[
            {"role": "system", "content": ANSWER_BUILDER_INSTRUCTIONS},
            {"role": "user", "content": ANSWER_BUILDER_MESSAGE_BUILD(message, '\n\n'.join(answers))}
        ]
    )
    return main_answer.choices[0].message.content



