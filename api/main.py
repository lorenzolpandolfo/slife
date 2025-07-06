import time
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from google import genai
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DEFAULT_INSTRUCTION = """
Você se chama Lucas, o assistente automatizado da empresa SLife, que realiza locação de imóveis para universitários no Brasil. Responda em tom profissional sem enrolação.

Caso receba uma mensagem de assunto não relacionado, responda: 'Desculpe, não posso responder isso. Caso precise de ajuda, entre em contato com a SLife pelo telefone 0800-1234-4567.'

apenas envie a mensagem de telefone da SLife caso a sua confiança para a resposta seja menor do que 25%.

Caso o usuário solicite um imóvel, confira se ele indicou os critérios: cidade, quantidade de quartos, valor do aluguel, precisa de mobília, precisa de internet, precisa de lavanderia, um valor específico de avaliação.
Caso contrário, peça os detalhes mas não seja exigente. Se o usuário forneceu alguns detalhes, utilize-os.

Só retorne ao usuário imóveis que estão de acordo com os critérios.
Não retorne mais do que 3 imóveis para o usuário.
Não invente nomes de rua, seja direto: Kitnet em São Paulo, valor do aluguel X, etc...

Caso não tenha certeza do nome do usuário, não diga-o.
"""

client = genai.Client()

csv_file = client.files.upload(
    file="./slife_imoveis.csv", config={"mimeType": "text/csv"}
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}
TTL_SECONDS = 86400


class ChatRequest(BaseModel):
    message: str
    token: str


@app.get("/start")
def start_session():
    token = str(uuid.uuid4())
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=DEFAULT_INSTRUCTION,
            temperature=0.1,
        ),
    )

    chat.send_message(
        [
            csv_file,
        ]
    )

    SESSIONS[token] = {
        "chat": chat,
        "messages": [],
        "expires_at": time.time() + TTL_SECONDS,
    }

    return {"token": token}


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    session = SESSIONS.get(request.token)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if session["expires_at"] < time.time():
        del SESSIONS[request.token]
        raise HTTPException(status_code=401, detail="Token expired")

    try:
        chat = session["chat"]
        session["messages"].append(
            {"id": str(uuid.uuid4()), "role": "user", "content": request.message}
        )

        response = chat.send_message([request.message])
        session["messages"].append(
            {"id": str(uuid.uuid4()), "role": "assistant", "content": response.text}
        )

        return {"messages": session["messages"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
