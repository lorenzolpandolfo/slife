from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

from google import genai
from google.genai import types


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


load_dotenv()

client = genai.Client()

csv_file = client.files.upload(
    file="./slife_imoveis.csv", config={"mimeType": "text/csv"}
)

chat = client.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=DEFAULT_INSTRUCTION,
        temperature=0.1,
    ),
)


response = chat.send_message(
    ["Segue a base de dados de imóveis da SLife. Se apresente formalmente.", csv_file]
)
print(response.text + "\n")


app = FastAPI()

if __name__ == "__main__":

    while True:
        msg = input("\n> Mensagem: ")
        response = chat.send_message([msg])
        print(response.text + "\n")
