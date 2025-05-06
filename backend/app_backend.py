import datetime
import os
import logging
import uvicorn
import llm
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_provider.MysqlDatabase import MysqlDatabase

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename='assistant-ia-db.log'
)

load_dotenv()
IP_HOST=os.getenv("IP_HOST")

# App Server Instance
app = FastAPI()

# Config CORS
origins = [
    'http://localhost:8501',  # Dirección de tu cliente Streamlit
]

# Permit connection from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapping and validation type data
class Message(BaseModel):
    message: str


# Point Chat
@app.post('/chat')
def chat_endpoint(msg: Message):
    try:
        request = msg.message
        print('Request:', request)
        logging.info(request)
        if request.lower().startswith("glpi:"):
            # RESPONSE OLLAMA ASSISTANT GLPI
            query_sql = llm.ask_to_sql(request)
            print(query_sql)
            logging.info(query_sql)
            if query_sql.startswith("SELECT"):
                mysql_db = MysqlDatabase()
                response_sql = mysql_db.query(query_sql)
                print(response_sql)
                logging.info(response_sql)
                response_ia = llm.result_sql_to_response(request, response_sql)
                current_date = datetime.datetime.now()
                print(response_ia)
                logging.info(response_ia)
                return {
                    'date_response': current_date.strftime('%d-%m-%Y %H:%M'),
                    'response': response_ia
                    }
            else:
                # RESPONSE ERROR QUERY SQL
                current_date = datetime.datetime.now()
                response = "No se ha podido procesar la consulta SQL."
                logging.info(response)
                return {
                    'date_response': current_date.strftime('%d-%m-%Y %H:%M'),
                    'response': response
                    }
        else:
            # RESPONSE OLLAMA ASSISTANT GENERAL
            response_ia = llm.assistant_chat(request)
            current_date = datetime.datetime.now()
            logging.info(response_ia)
            return {
                'date_response': current_date.strftime('%d-%m-%Y %H:%M'),
                'response': response_ia
                }
    except Exception as e:
        current_date = datetime.datetime.now()
        return {
            'date_response': current_date.strftime('%d-%m-%Y %H:%M'),
            'response': "Error al ejecutar la consulta sql."
        }


# Point WebSocket Chat IA Assintent
@app.websocket('/ws/chat')
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    # ID for client
    client_id = str(uuid.uuid4())[:8]
    logging.info(f'Client [{client_id}] connect OK!')
    while True:
        try:
            # Receiever message
            data = await websocket.receive_text()
            # Si receiver message "ping", send responde "pong"
            if data == 'ping':
                logging.info('Receiver Message: ping')
                await websocket.send_text('pong')
                logging.info('Sending Message: pong')
            else:
                print(f'[{client_id}] request:', data)
                # RESPONSE OLLAMA
                query_sql = llm.ask_to_sql(data)
                print(query_sql)
                mysql_db = MysqlDatabase()
                response_sql = mysql_db.query(query_sql)
                print(response_sql)
                response_ia = llm.result_sql_to_response(data, response_sql)
                print('Bot IA: ', response_ia)
                await websocket.send_text(response_ia)
        except Exception as e:
            logging.warning(f'Error Unexpected [{client_id}]: {e}')
        except WebSocketDisconnect:
            logging.info(f'Disconnected Client [{client_id}]: {e}')
        finally:
            logging.info(f'Finishing connection WebSocket! [{client_id}]')


# Run Server FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host=IP_HOST, port=8000, ws_ping_timeout=300)
