import logging
import os
import requests
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from prompts import prompt_assistant_to_sql

from db_provider.MysqlDatabase import MysqlDatabase

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
        query_sql = chat(question)
        try:
            mysql_db = MysqlDatabase()
            response = mysql_db.query(query_sql)
            print('Bot IA: ', f'{question}')
            print(extract_result_query(response))
        except Exception as e:
            error = f'Error occurred, {e}'
            logger.error(error)


def chat(question) -> str | None:
    url = ENDPOINT_LLM
    model = MODEL_LLM
    messages = [
        {
            'role': 'system',
            'content': prompt_assistant_to_sql

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
        return ''
    except ValidationError as ve:
        error = f'Error parser response {ve}'
        logger.error(error)
        return ''

# Extract and show result query
def extract_result_query(response):
    for item in response:
        for i in item.values():
            print(i)


if __name__ == '__main__':
    main()
