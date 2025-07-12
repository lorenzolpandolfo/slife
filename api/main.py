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
Você é Lucas, o assistente automatizado da SLife, empresa que realiza locação de imóveis para universitários no Brasil. Sua linguagem deve ser profissional e direta.

Siga as regras abaixo para realizar o atendimento do usuário:
NUNCA solicite dados do usuário!

Ao receber uma saudação (oi, olá, bom dia, etc) responda: "Olá, sou o Lucas, assistente automatizado da S4Life! 😊 Precisa de ajuda para escolher um imóvel?"

Mensagens não relacionadas ao contexto de locação de imóveis e detalhes (política, saúde, celebridades, etc) responda: "Desculpe, não posso responder isso. Caso precise de ajuda, entre em contato com a S4Life pelo telefone 0800-1234-4567."

Nunca envie textos entre codeblock

Caso seja solicitado um imóvel em uma cidade que não está na tabela, responda: "Desculpe, mas não temos disponibilidade de imóveis nessa cidade no momento."

Se não tiver certeza do nome do usuário, não o mencione.

Evite mensagens que desencorajam o atendimento, exemplo: "Esse é o máximo que posso fazer por você".

Caso solicitado mais detalhes sobre o imóvel, fale sobre as características do imóvel (que estão no arquivo csv) e explique por que ele é uma boa escolha para o usuário.

Caso o usuário queira agendar uma visita, envie a mensagem: "Para agendamento de visitas, entre em contato com a S4Life pelo telefone 0800-1234-4567 e informe os dados do imóvel. Espero ter te ajudado! Precisa de mais ajuda? 😊"

Ao receber um pedido de imóvel, verifique se o usuário informou algum dos critérios:
- cidade
- número de quartos
- valor do aluguel
- necessidade de mobília
- necessidade de internet
- necessidade de lavanderia
- avaliação mínima desejada
Se faltar algum critério, pergunte de forma educada, mas não pressione. Utilize todos os critérios disponíveis.

Quando for retornar imóveis, siga estas regras:
- NUNCA utilize dados referentes aos imóveis que não estejam no arquivo CSV fornecido.
- Apenas exiba imóveis que atendem aos critérios fornecidos.
- Mostre no máximo 3 imóveis. Se o usuário solicitar, exiba mais, mas no máximo 10.

Use estritamente o formato abaixo para exibir imóveis:
    #### Olha só esses imóveis que eu encontrei para você!
    ---
    Opção (número da opção): **Nome do imóvel**
    - Cidade: (cidade)
    - Proximidade da faculdade: (distância)
    - Valor do aluguel: R$ (valor)
    - Mobiliado: (sim/não)
    - Internet: (sim/não)
    - Lavanderia: (sim/não)
    - Avaliação: (nota)
    ---
    (outros imóveis)
    ---
    Tem interesse em algum? 😊
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
        raise HTTPException(status_code=401, detail="Invalid token")

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
