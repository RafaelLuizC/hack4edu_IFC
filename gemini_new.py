from google import genai
from google.genai import types
import base64
import os

import json, os, dotenv, time, sys
from util.helpers import *
from util.prompts import *
#from AI.qwen3 import ia_local
from processing.pdf import extrair_dados_pdf

dotenv.load_dotenv()
project = str (os.getenv("ID_PROJETO"))
location = str (os.getenv("LOCALIZACAO"))

prompt_ocr = """Corrija o seguinte texto que foi extraído via OCR, possivelmente contendo erros de reconhecimento de caracteres. Ajuste o texto para que fique legível e accurate, corrigindo caracteres especiais, palavras mal interpretadas, e problemas de formatação. Mantenha o conteúdo original tanto quanto possível, mas faça as correções necessárias para melhorar a clareza e precisão. Retorne apenas o texto corrigido, sem comentários adicionais. Texto a ser corrigido:"""

prompt_perguntas = """Você é um gerador de perguntas e deverá criar uma pergunta de múltipla escolha sobre o texto de referencia enviado. A pergunta deve ter 4 opções de resposta, onde uma delas será a correta. Cada resposta deve ter uma explicação do porquê está errada ou correta.
  Com base no texto enviado, traduza ele para a lingua Portuguesa e conte a historia de maneira ludica para crianças, focando no ensino do conteudo apresentado no material.
  Passos: Leia a historia e compreenda o contexto.
  Analise ela e crie uma pergunta de múltipla escolha com base no texto. 
  Regras: Escreva somente utilizando texto corrido, não utilize topicos.
  Utilze uma linguagem simples e de facil compreensão.
  Analise o texto e corrija eventuais erros de gramatica.
  Utilize o texto para aprendizado de Ingles, inclua exemplos de como as palavras são em portugues e ingles dentro da historia, sem modificar a estrutura dela.
  Use a historia para ensinar Ingles!
    {{
      "Pergunta": "Texto da pergunta",
      "Resposta1": "Texto da resposta1 (explicação do erro)",
      "Resposta2": "Texto da resposta2 (explicação do erro)",
      "Resposta3": "Texto da resposta3 (explicação do erro)",
      "Resposta4": "Texto da resposta correta (correta)"
    }}
  - Apenas uma resposta deve ser marcada como correta e acompanhada da explicação.
  - As demais respostas devem incluir uma explicação do erro cometido."""

def generate(string, prompt_regras):
  client = genai.Client(
            vertexai=True,
            project=project,
            location=location, 
        )
    
  msg1_text1 = types.Part.from_text(text=f"{string}")
  si_text1 = f"""{prompt_regras}"""

  model = "gemini-2.5-flash-lite"
  contents = [
    types.Content(
      role="user",
      parts=[
        msg1_text1
      ]
    ),
  ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 65535,
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    system_instruction=[types.Part.from_text(text=si_text1)],
    thinking_config=types.ThinkingConfig(
      thinking_budget=0,
    ),
  )

  result_text = ""
  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    if hasattr(chunk, "text"):
      result_text += chunk.text

  return result_text

if __name__ == "__main__":

    os.makedirs("output", exist_ok=True)
    correcao_ocr_path = "output/correcao_ocr_lista1.txt"
    texto_referencia = "pdf_sample/LISTA_1__MEDIDAS_DESCRITIVAS___Estatstica.pdf"

    if os.path.exists(correcao_ocr_path):
      # Se o arquivo corrigido já existe, leia dele
      print ("Lendo texto corrigido existente...")
      with open(correcao_ocr_path, "r", encoding="utf-8") as f:
        texto_corrigido = f.read()
    else:
      print ("Lendo texto do PDF...")
      # Se não existe, extraia o texto do PDF e gere a correção
      texto_extraido = extrair_dados_pdf(texto_referencia)
      texto_extraido = ' '.join(texto_extraido)
      texto_corrigido = generate(texto_extraido, prompt_ocr)
      print(texto_corrigido)
      with open(correcao_ocr_path, "w", encoding="utf-8") as f:
        f.write(str(texto_corrigido))


    print(f"O tipo da variavel texto_corrigido é: {type(texto_corrigido)}")
    if type(texto_corrigido) == list:
      texto_corrigido = ' '.join(texto_corrigido)
    else:
      texto_corrigido = str(texto_corrigido)

    texto_perguntas = generate(texto_corrigido, prompt_perguntas)

    print(texto_perguntas)