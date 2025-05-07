from typing import AnyStr
import datetime
import time
import json
import os
import threading
import logging
import streamlit as st
from dotenv import load_dotenv
from websocket import create_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()
URL_SERVER_FASTAPI_BACKEND=os.getenv("URL_SERVER_FASTAPI_BACKEND")

# Function load and save history file JSON
HISTORY_FILE = "chat_history_messages_ws.json"

# Function load messages history
def load_history() -> json:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# Function save messages history
def save_history(history) -> None:
    with open(HISTORY_FILE, "w") as f:
        json.dump(history or [], f, ensure_ascii=False, indent=2)

# Initial State
if "ws" not in st.session_state:
    st.session_state.ws = None
# Thread ping server
if "ping_thread_started" not in st.session_state:
    st.session_state.ping_thread_started = False
# Chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
# Load history from file JSON
if "history" not in st.session_state:
    st.session_state.chat_history = load_history()


# Function show message html
def show_message_html(author: str, date_message: datetime, message: str, chat_html) -> str:
    if author == "Tú":
        chat_html += f"""<div class='user message'>
                            🧑 <span class='date-message'>{date_message}</span>
                            <div>{message}</div>
                        </div>"""
    else:
        chat_html += f"""<div class='assistant message'>
                            🤖 <span class='date-message'>{date_message}</span>
                            <div>{message}</div>
                        </div>"""
    return chat_html


# Send pings from connection active of Server FastAPI
def send_pings(ws: AnyStr) -> None:
    logging.info("Ping thread started...")
    while True:
        try:
            ws.send("ping")
            logging.info(f"Request: Sending Ping")
            response = ws.recv()
            logging.info(f"Response: {response}")
        except Exception as e:
            logging.error("Error send ping:",e)
            break
        time.sleep(30)


# Function to connect WebSockets (sin button)
def connect_ws() -> None:
    if st.session_state.ws is None:
        try:
            ws = create_connection("ws://127.0.0.1:8000/ws/chat")
            st.session_state.ws = ws
            st.session_state.chat_log = []
        except Exception as e:
            logging.error("Error Connect WebSocket:", e)

# Call connect WebSocket
connect_ws()

# Launch threading ping if not init
if not st.session_state.ping_thread_started and st.session_state.ws:
    threading.Thread(target=send_pings, args=(st.session_state.ws,), daemon=True).start()
    st.session_state.ping_thread_started = True


##### Page Web #####
st.set_page_config(page_title="Chat IA - Soporte Tickets", page_icon=None)
# Title Page
st.title("💬 Asistente IA WS - Soporte Tickets")
# Question User Input
question_user = st.text_area("Escribe tu consulta:", key="input_user",  placeholder= "Aqui tu consulta", height=75)
current_date = datetime.datetime.now()
# If Click Btn Enviar
if st.button("Enviar") and question_user:
    date_question_user = current_date.strftime('%d-%m-%Y %H:%M')
    # Send and wait server response
    if st.session_state.ws:
        try:
            with st.spinner("Esperando respuesta IA ..."):
                st.markdown('')
                ws = st.session_state.ws
                # Send request assistant IA Server
                ws.send(question_user)
                # Response assistant IA Server
                response = ws.recv()
                # Convert string json a object json
                response_json = json.loads(response)
                date_response = response_json['date_response']
                data_response = response_json['response']
            # Add to History
            st.session_state.chat_history.append({
                "role": "Tú",
                "timestamp": date_question_user,
                "message": question_user
            })
            st.session_state.chat_history.append({
                "role": "Bot",
                "timestamp": date_response,
                "message": data_response
            })
            st.session_state.current_response = ""
            # Save History from JSON
            save_history(st.session_state.chat_history)
        except Exception as e:
            st.error("Error communication WebSocket:",e)
    else:
        st.warning("No Have connection websocket active!.")


# Show history conversation
st.markdown("")
st.markdown("")
st.markdown("🗨️ Historial del chat")
# Create container for chat with scroll
st.markdown("""
    <style>
        .chat-container {
            height: 600px;
            overflow-y: auto;
            background-color: transparent;
            display: flex;
            flex-direction: column; /* Invertir mensajes (últimos arriba) junto con display */
        }
        .user { 
            align-self: flex-end;
            background-color: #d1e7dd;
            color: #000;
            text-align: right;
            margin-right: 8px;
        }
        .assistant {
            align-self: flex-start;
            background-color: #e2e3e5;
            color: #000;
            text-align: left;   
        }
        .message {
            max-width: 100%;
            padding: 10px 15px;
            border-radius: 10px;
            margin: 5px 0;
            font-size: 15px;
            word-wrap: break-word;
        }
        .date-message {
            font-size: 0.8em;
        }
    </style>
""", unsafe_allow_html=True)
chat_html = '<div class="chat-container">'
for entry in reversed(st.session_state.chat_history):
    author = entry["role"]
    date_message = entry["timestamp"]
    message = entry["message"]
    chat_html = show_message_html(author, date_message, message, chat_html)
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)
