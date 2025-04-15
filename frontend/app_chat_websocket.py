from typing import AnyStr
import time
import threading
import logging
import streamlit as st
from websocket import create_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Initial State
if "ws" not in st.session_state:
    st.session_state.ws = None
# Thread ping server
if "ping_thread_started" not in st.session_state:
    st.session_state.ping_thread_started = False
# Chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


#Show messages with icons
def show_message(author: str, text: str) -> None:
    if author == "Tú":
        st.markdown(
            f"""
            <div style='text-align: right;'>
                <span>🧑 {text} </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='text-align: left;'>
                <span>🤖 {text} </span>
            </div>
            """,
            unsafe_allow_html=True
        )


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

# Title Page
st.title("💬 Asistente IA WS - Tickets Soporte")
# Question User Input
question_user = st.text_input("Escribe tu consulta:", key="input_user",  placeholder= 'Aqui tu consulta')
# If Click Btn Enviar
if st.button("Enviar") and question_user:
    # Send and wait server response
    if st.session_state.ws:
        try:
            with st.spinner("Esperando respuesta IA ..."):
                st.markdown('')
                ws = st.session_state.ws
                ws.send(question_user)
                response = ws.recv()
            st.session_state.chat_log.append(("Tú", question_user))
            st.session_state.chat_log.append(("Bot", response))
            st.session_state.current_response = ""
        except Exception as e:
            st.error("Error communication WebSocket:",e)
    else:
        st.warning("No Have connection websocket active!.")

# Show history conversation
for author, text in st.session_state.chat_log:
    show_message(author, text)
    # st.markdown(f'🤖 {author}: {text}')
