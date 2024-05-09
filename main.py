import json
from fastapi import FastAPI, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from utils.utilities import (
    ConversationalMemory,
    UsersDb,
    get_weather,
    get_weather_by_coordinates,
)
from utils.config import UserInput, start_message, function_descriptions

# Initailizing FastAPI
app = FastAPI()

# Adding CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initializing OpenAI agent
client = OpenAI()

# Default starting message
messages = [
    {
        "role": "system",
        "content": start_message,
    },
]

Memory = ConversationalMemory(messages)

# Initializing Database
db = UsersDb("./db/Users.db")


def RunAgentFunction(func_name: str, func_arguments: dict):
    function = eval(func_name)
    result_from_function = function(func_arguments)
    return result_from_function


def predictOutput(messages: list[dict], user_email: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        function_call="auto",
        functions=function_descriptions,
        temperature=0.3,
    )

    res = response.choices[0]
    if res.finish_reason == "function_call":
        func_name = res.message.function_call.name
        func_args = json.loads(res.message.function_call.arguments)

        # Run agent function
        results = RunAgentFunction(func_name, func_args)

        messages = Memory.agentGet(
            {"role": "function", "name": func_name, "content": results},
            messages,
        )

        agent_response = predictOutput(messages, user_email)

        return agent_response
    else:
        agent_response = res.message.content

        # Adding to Memory
        messages = Memory.agentGet(
            {"role": "assistant", "content": agent_response}, messages
        )

        # Updating user chat history
        db.add_message(user_email, agent_response, "assistant")

        return agent_response


@app.post("/chat")
async def chat(msg: UserInput):
    if not msg.user_email:
        raise HTTPException(status_code=400, detail="Email not provided")

    message = {"role": "user", "content": msg.user_message}

    # Getting chat history
    chat_history = db.getUserChatHistory(msg.user_email)

    if chat_history:
        messages = [
            {
                "role": (
                    "system"
                    if data[0] == "system"
                    else ("assistant" if data[0] == "assistant" else "user")
                ),
                "content": data[1],
            }
            for data in chat_history
        ]

        messages.append(message)

        db.add_message(msg.user_email, msg.user_message, "user")
        res = predictOutput(messages, msg.user_email)

        return {"message": res}
    else:
        message = [
            {
                "role": "system",
                "content": start_message,
            },
            {
                "role": "user",
                "content": msg.user_message,
            },
        ]

        db.add_message(msg.user_email, start_message, "system")
        db.add_message(msg.user_email, msg.user_message, "user")
        res = predictOutput(message, msg.user_email)

        return {"message": res}


@app.get("/weather")
async def weather(long: str, lat: str):
    # Getting weather condition
    weather_condition = get_weather_by_coordinates(long, lat)

    messages = [
        {
            "role": "system",
            "content": """
            You would be giving some weather condition, base on whether conditions determine is its advisable to irrigate a field
            
            Your response should be brief and in the following format:
            Base on the weather condition, would be advisable to irrigate the field. with some few suggestions
            """,
        },
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0.3,
    )

    res = response.choices[0].message.content

    return {"weather": weather_condition, "Advice": res}
