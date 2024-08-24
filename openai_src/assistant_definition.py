import json, time

from openai_src.native_assistant import client
from openai_src.functions import get_question_answer

class OpenAiBot:

  def __init__(self, assistant):
    self.assistant = assistant
    self.question_and_answer_history = []

  def handle_requires_action_status(self, run):
    while run.status == "requires_action":
      tool_outputs = []

      for tool in run.required_action.submit_tool_outputs.tool_calls:
          if tool.function.name == "get_question_answer":
              result = get_question_answer([self.question_and_answer_history[-1]] if self.question_and_answer_history else [], **json.loads(tool.function.arguments))
          else:
            raise Exception("Unknown function:", tool.function_name)
          tool_outputs.append(
              {"tool_call_id": tool.id, "output": json.dumps(result)}
          )

      # Submit the tool outputs
      if tool_outputs:
          run = client.beta.threads.runs.submit_tool_outputs_and_poll(
              thread_id=self.thread.id, run_id=run.id, tool_outputs=tool_outputs
          )
      else:
          raise Exception("No tool outputs to submit.")

  def get_assistant_msg(self):
    run = client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )

    if run.status == "requires_action":
      self.handle_requires_action_status(run)

    while run.status not in ["completed", "failed"]:
      time.sleep(2)
      run = client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)

    if run.status == "completed":
      messages = client.beta.threads.messages.list(thread_id=self.thread.id)
      self.question_and_answer_history.append({
        "question": messages.data[1].content[0].text.value,
        "answer": messages.data[0].content[0].text.value
      })
      return messages.data[0].content[0].text.value
    else:
      raise Exception(f"Run ended with status: {run.status}")

  def start_conversation(self, assistant_welcome_msg):
    self.thread = client.beta.threads.create()
    self.question_and_answer_history = []
    self.send_msg('assistant', assistant_welcome_msg)

  def chat(self, user_msg):
    self.send_msg('user', user_msg)

    response = self.get_assistant_msg()
    return response

  def send_msg(self, role, msg):
    _ = client.beta.threads.messages.create(
      self.thread.id,
      role=role,
      content=msg,
    )