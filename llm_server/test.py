from app import main
import guidance, inspect

# set the default language model used to execute guidance programs
endpoint = "http://localhost:8000/v1/chat"

llm = guidance.llms.OpenAI(
    "gpt-3.5-turbo", chat_mode=True, rest_call=True, caching=False, endpoint=endpoint
)
llm.endpoint = endpoint

program = guidance(
    """
{{#user~}}
What is the capital of {{country}}?
{{~/user}}
{{#assistant~}}
{{gen 'answer' temperature=0.3 max_tokens=12}}
{{~/assistant}}
"""
)

r = program(llm=llm, country="Canada", silent=True)
r

print("Result: ", r)
