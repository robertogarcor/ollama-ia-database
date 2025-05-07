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
    filename='backend-ws.log'
)

load_dotenv()
IP_HOST=os.getenv("IP_HOST")

# App Server Instance
app = FastAPI()

# Config CORS
origins = [
    'http://localhost:8501',  #Dirección de tu cliente Streamlit
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


# Point WebSocket Chat IA Assistant
@app.websocket('/ws/chat')
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    # ID for client
    client_id = str(uuid.uuid4())[:8]
    logging.info(f'Client [{client_id}] connect OK!')
    while True:
        try:
            # Receiver message
            data = await websocket.receive_text()
            # Si receiver message "ping", send response "pong"
            if data == 'ping':
                # logging.info('Receiver Message: ping')
                await websocket.send_text('pong')
                # logging.info('Sending Message: pong')
            else:
                print(f'[{client_id}] request:', data)
                if data.lower().startswith("glpi:"):
                    # RESPONSE OLLAMA ASSISTANT Technical
                    query_sql = llm.ask_to_sql(data)
                    print(query_sql)
                    logging.info(query_sql)
                    if query_sql.startswith("SELECT"):
                        mysql_db = MysqlDatabase()
                        response_sql = mysql_db.query(query_sql)
                        print(response_sql)
                        logging.info(response_sql)
                        response_ia = llm.result_sql_to_response(data, response_sql)
                    else:
                        # RESPONSE ERROR QUERY SQL
                        response_ia = "No se ha podido procesar la consulta SQL."
                    current_date = datetime.datetime.now()
                    response_ia_json = {
                        'date_response': current_date.strftime('%d-%m-%Y %H:%M'),
                        'response': response_ia
                    }
                    print('Bot IA: ', response_ia_json)
                    logging.info(f'Bot IA: {response_ia_json}')
                    await websocket.send_json(response_ia_json)
                else:
                    # RESPONSE OLLAMA ASSISTANT GENERAL
                    response_ia = llm.assistant_chat(data)
                    current_date = datetime.datetime.now()
                    response_ia_json = {
                        'date_response': current_date.strftime('%d-%m-%Y %H:%M'),
                        'response': response_ia
                    }
                    print('Bot IA: ', response_ia_json)
                    logging.info(f'Bot IA: {response_ia_json}')
                    await websocket.send_json(response_ia_json)
        except Exception as e:
            print(f'Error Unexpected [{client_id}]: {e}')
        except WebSocketDisconnect:
            print(f'Disconnected Client [{client_id}]: {e}')
        finally:
            pass
            print(f'Finishing connection WebSocket! [{client_id}]')


# Run Server FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, ws_ping_timeout=300)
