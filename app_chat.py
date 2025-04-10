import logging
import os
import requests
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

ENDPOINT_LLM = os.getenv('URL_SERVER_OLLAMA_LOCAL')
MODEL_LLM = os.getenv('MODEL_OLLAMA_LOCAL')

class Message(BaseModel):
    role: str
    content: str

def main() -> None:
    while True:
        question = input('User: ')
        if question.lower() == 'quit' or question.lower() == 'q':
            print('Adios!')
            break
        response = chat(question)
        print('IA: ', response)
        print()


def chat(question) -> str | None:
    url = ENDPOINT_LLM
    model = MODEL_LLM
    messages = [
        {
            'role': 'system',
            'content': 'Te llamas Llama y eres una persona ironica. Experto en BBDD',
        },
        {
            'role': 'user',
            'content': question,
        },
    ]
    try:
        response = requests.post(
            url,
            json={
                'model': model,
                'messages': messages,
                'stream': False,
            },
        )
        response.raise_for_status()
        response_json = response.json()
        message = Message(**response_json['message'])
        return message.content
    except requests.RequestException as e:
        print(f'Error occurred: {e}')
        return None
    except ValidationError as ve:
        print(f'Error parser response {ve}')
        return None


if __name__ == '__main__':
    main()
