import datetime
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit.components.v1 import html

load_dotenv()
URL_SERVER_FASTAPI_BACKEND=os.getenv("URL_SERVER_FASTAPI_BACKEND")

# Function load and save history file JSON
HISTORY_FILE = "chat_history_messages.json"

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


# Chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
# Load history from file JSON
if "history" not in st.session_state:
    st.session_state.chat_history = load_history()
    # st.write("🔁 Historial cargado:", st.session_state.chat_history)

##### Page Web #####

st.set_page_config(page_title="Chat IA - Soporte Tickets", page_icon=None)
st.title("💬 Asistente IA - Soporte Tickets")
# Question User Input
question_user = st.text_input('Escribe tu consulta:', key='user_input', placeholder='Aqui tu consulta')
current_date = datetime.datetime.now()
# If Click Btn Enviar and question user true
if st.button("Enviar") and question_user:
    date_question_user = current_date.strftime('%d-%m-%Y %H:%M')
    # Send message to backend FastAPI
    try:
        with st.spinner("Esperando respuesta IA ..."):
            response = requests.post(
                URL_SERVER_FASTAPI_BACKEND + "/chat",
                json={"message": question_user}
            )
            # Response assistant IA Server
            date_response = response.json()['date_response']
            data_response = response.json()['response']
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
        st.error(f'Error Connection Server: {e}')


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










