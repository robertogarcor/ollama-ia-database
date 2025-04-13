import streamlit as st
import requests


#Show messages with icons
def show_message(author, text):
    if author == "Tú":
        st.markdown(
            f"""
            <div style='text-align: left;'>
                <span>🧑 {text} </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='text-align: right;'>
                <span>🤖 {text} </span>
            </div>
            """,
            unsafe_allow_html=True
        )


# Page Web

st.title('💬 Chat simple con FastAPI')

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input('Escribe tu consulta:')

if st.button('Enviar') and user_input:
    # Send message to backend FastAPI
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": user_input}
        )
        request = response.json()["response"]

        # Add to History
        st.session_state.chat_history.append(("Tú", user_input))
        st.session_state.chat_history.append(("Bot", request))
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")

# Show history conversation
for author, text in st.session_state.chat_history:
    show_message(author, text)
    # st.markdown(f'🤖 {author}: {text}')



