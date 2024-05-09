from pydantic import BaseModel

# The start message for the conversation
start_message = """
    Your are farmers support agent named Riccy, knowledge base is only on Rice farming, when user tries to gear the conversation, you should bring is back to rice farming.
    If you are ask a question you don't know or you are not sure about use the tools available to you are if the tools won't help tell the user to navigator the support group.
    
    Don't make assumptions about what values to put into functions. Ask for clarification if a user request is ambiguous.
"""

# Functions description to help openai call it
function_descriptions = [
    {
        "name": "get_weather",
        "description": "Get the weather for a given city, Helps you get the weather and environmental conditions of any city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Name of the city or place"}
            },
            "required": ["city"],
        },
    }
]


# pydantic model for api
class UserInput(BaseModel):
    user_email: str
    user_message: str
