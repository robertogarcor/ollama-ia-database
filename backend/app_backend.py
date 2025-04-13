import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

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
@app.post("/chat")
def chat_endpoint(msg: Message):
    user_msg = msg.message
    response = f"Hola, tú dijiste: '{user_msg}'"
    return {"response": response}


# Run FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)