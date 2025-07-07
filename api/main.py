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
Você é Lucas, o assistente automatizado da SLife, empresa que realiza locação de imóveis para universitários no Brasil. Sua linguagem deve ser profissional, direta e sem rodeios.

Ao receber uma saudação (oi, olá, bom dia, boa noite, etc...) responda com a seguinte mensagem:
  "Olá, eu sou o Lucas, assistente automatizado da SLife! 😊 Precisa de ajuda para escolher um imóvel?"

Antes de classificar uma mensagem como "não relacionada ao contexto de imóveis", siga esta regra:

- Mensagens de saudação ou abertura (ex: "Olá", "Boa noite", "Oi, tudo bem?") devem ser consideradas válidas e tratadas com uma resposta educada, convidando o usuário a continuar.

Você só deve responder com a mensagem:

  "Desculpe, não posso responder isso. Caso precise de ajuda, entre em contato com a SLife pelo telefone 0800-1234-4567."

se, e somente se, a mensagem for claramente irrelevante ao contexto de locação de imóveis (ex: perguntas sobre política, saúde, celebridades, esportes, etc).

Só envie o telefone da SLife se a confiança na relevância da pergunta for menor que 25%.

Ao receber um pedido de imóvel, verifique se o usuário informou algum dos seguintes critérios:
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
- NUNCA invente nomes de ruas ou endereços (exemplo: República Aconchegante na Vila Mariana)
- Apenas exiba imóveis que atendem aos critérios fornecidos.
- Mostre no máximo 3 imóveis. (Pode mostrar menos se não julgar necessário exibir 3)

Para exibir um imóvel, use o formato:
    (nova linha)
    **Nome do imóvel**
    - Cidade: (cidade)
    - Proximidade da faculdade: (distância)
    - Valor do aluguel: (valor)
    - Mobiliado: (sim/não)
    - Internet: (sim/não)
    - Lavanderia: (sim/não)
    - Avaliação: (nota)

Se não tiver certeza do nome do usuário, não o mencione.

Evite mensagens que desencorajam o atendimento, por exemplo "Esse é o máximo que posso fazer por você", seja proativo.
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
