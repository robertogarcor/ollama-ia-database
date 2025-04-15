import os
import json
import requests
import streamlit as st

# Function load and save history file JSON
HISTORY_FILE = "chat_history_messages.json"

# Function load messages history
def load_history() -> json:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Function save messages history
def save_history(history) -> None:
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

#Show messages with icons
def show_message(author: str, message: str) -> None:
    if author == "Tú":
        st.markdown(
            f"""
            <div class='user'>
                <span>🧑 {message} </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class='assistant'>
                <span>🤖 {message} </span>
            </div>
            """,
            unsafe_allow_html=True
        )

def show_message_html(author: str, message: str, chat_html) -> str:
    if author == "Tú":
        chat_html += f"<div class='user message'>🧑 {message} </div>"
    else:
        chat_html += f"<div class='assistant message'>🤖 {message}</div>"
    return chat_html


# Chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
# Load history from file JSON
if "history" not in st.session_state:
    st.session_state.chat_history = load_history()
    # st.write("🔁 Historial cargado:", st.session_state.chat_history)

##### Page Web #####

st.title("💬 Asistente IA - Tickets Soporte")
# Question User Input
question_user = st.text_input('Escribe tu consulta:', key='uer_input', placeholder='Aqui tu consulta')
# If Click Btn Enviar and question user true
if st.button("Enviar") and question_user:
    # Send message to backend FastAPI
    try:
        with st.spinner("Esperando respuesta IA ..."):
            response = requests.post(
                'http://127.0.0.1:8000/chat',
                json={"message": question_user}
            )
            # Response assistant IA Server
            response = response.json()['response']
        # Add to History
        st.session_state.chat_history.append(("Tú", question_user))
        st.session_state.chat_history.append(("Bot", response))
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
            flex-direction: column;
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
            border-radius: 20px;
            margin: 5px 0;
            font-size: 15px;
            word-wrap: break-word;
        }
    </style>
""", unsafe_allow_html=True)
chat_html = '<div class="chat-container">'
for author, message in st.session_state.chat_history:
    chat_html = show_message_html(author, message, chat_html)
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)










