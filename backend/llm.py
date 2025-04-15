import logging
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import prompts

load_dotenv()
logger = logging.getLogger(__name__)

ENDPOINT_LLM = os.getenv('URL_SERVER_OLLAMA_LOCAL')
MODEL_LLM = os.getenv('MODEL_OLLAMA_LOCAL')


class Message(BaseModel):
    role: str
    content: str

# Pasar pregunta (question) del usuario al modelo para crear consulta
def ask_to_sql(question) -> str | None:
    url = ENDPOINT_LLM
    model = MODEL_LLM
    messages = [
        {
            'role': 'system',
            'content': prompts.prompt_assistant_to_sql

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
                'options': {
                    "temperature": 0
                }
            },
        )
        response.raise_for_status()
        response_json = response.json()
        message = Message(**response_json['message'])
        return message.content
    except requests.RequestException as e:
        error = f'Error occurred, {e}'
        logger.error(error)
        return None
    except ValidationError as ve:
        error = f'Error parser response {ve}'
        logger.error(error)
        return None


# Pasar la consulta del usuario y resultado de la consulta al modelo
# para generar una respuesta por el modelo
def result_sql_to_response(question, response_sql) -> str | None:

    user_message = f'##3 CONSULTA USER: {question}\n### RESULTADOS DE LA BASE DE DATOS: {response_sql}'

    url = ENDPOINT_LLM
    model = MODEL_LLM
    messages = [
        {
            'role': 'system',
            'content': prompts.prompt_result_to_response
        },
        {
            'role': 'user',
            'content': user_message,
        },
    ]
    try:
        response = requests.post(
            url,
            json={
                'model': model,
                'messages': messages,
                'stream': False,
                'options': {
                    "temperature": 0
                }
            },
        )
        response.raise_for_status()
        response_json = response.json()
        message = Message(**response_json['message'])
        return message.content
    except requests.RequestException as e:
        error = f'Error occurred, {e}'
        logger.error(error)
        return None
    except ValidationError as ve:
        error = f'Error parser response {ve}'
        logger.error(error)
        return None