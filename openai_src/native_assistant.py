from openai import OpenAI

from openai_src.constants import OPENAI_API_KEY, ASSISTANT_ID_TO_RETRIVE
from openai_src.constants import ASSISTANT_INSTRUCTIONS, ASSISTANT_NAME_TO_CREATE, ASSISTANT_MODEL, ASSISTANT_TEMPERATURE

client = OpenAI(
    api_key=OPENAI_API_KEY
)

def get_assistant(assistant_id_to_retrive, assistant_name_to_create):
  if assistant_id_to_retrive:
    assistant = client.beta.assistants.retrieve(assistant_id_to_retrive)
  elif assistant_name_to_create:
    assistant = client.beta.assistants.create(
        instructions=ASSISTANT_INSTRUCTIONS,
        name=assistant_name_to_create,
        # tools=ASSISTANT_TOOLS,
        model=ASSISTANT_MODEL,
        temperature=ASSISTANT_TEMPERATURE
    )
  else:
    raise Exception("assistant_id_to_retrive is None and assistant_name_to_create is None")

  return assistant

assistant = get_assistant(ASSISTANT_ID_TO_RETRIVE, ASSISTANT_NAME_TO_CREATE)