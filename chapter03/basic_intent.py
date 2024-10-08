import openai
import os

from dotenv import load_dotenv

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import uvicorn


app = fastapi.FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# 얘는 자바의 DTO 역할
class ChatInput(BaseModel):
    message: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 300
    temperature: float = 0.9


# fast api 에서 씀
class LlmTemplate(BaseModel):
    message: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 300
    temperature: float = 0.9
    system_message: str = "You are an AI assistant."


def llm_for_chat(llm: LlmTemplate) -> str:
    response = openai.chat.completions.create(
        model=llm.model,
        messages=[
            {"role": "system", "content": llm.system_message},
            {"role": "user", "content": llm.message},
        ],
        max_tokens=llm.max_tokens,
        temperature=llm.temperature,
    )

    return response.choices[0].message.content


INTENT_CLASSIFIER_PERSONA = "you are a helpful intent classifier, you job is to classify the intent of the user message."
ASSISTANT_PERSONA = "you are a helpful assistant, your job is to answer user's inquiry"


@app.post("/chat")
def chat(input: ChatInput) -> str:

    DEAFULT_RESPONSE = f"""
    I'm sorry, I am not able to understand your message.
    """

    INTENT_PROMPT = f"""
    choose the one of the following intents for the user message
    - purchase
    - inquiry
    - complaint

    User: I have a problem, your service is aweful
    classifier: complaint

    User: {input.message}
    classifier: 

    """

    intent_llm = LlmTemplate(
        message=INTENT_PROMPT,
        model=input.model,
        max_tokens=input.max_tokens,
        temperature=input.temperature,
        system_message=INTENT_CLASSIFIER_PERSONA,
    )

    intent = llm_for_chat(intent_llm)

    print(intent)

    if intent == "complaint":
        COMPLAINT_RESPONSE = f"""
        I'm sorry to hear that you're having trouble.
        """
        return COMPLAINT_RESPONSE

    if intent == "purchase":
        PURCHASE_RESPONSE = f"""
        I see your order.
        """
        return PURCHASE_RESPONSE
    
    if intent == "inquiry":
       
       inquiry_llm = LlmTemplate(
           message=input.message,
           model=input.model,
           max_tokens=input.max_tokens,
           temperature=input.temperature,
           system_message=ASSISTANT_PERSONA,
       )
       return llm_for_chat(inquiry_llm)

    return DEAFULT_RESPONSE


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
