from google import genai
from google.genai import types
import base64

import os, dotenv, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #Serve para importar a pasta raiz.

from util.helpers import *
from util.prompts import *
from databases.bd_utils import *

dotenv.load_dotenv()
project = str (os.getenv("ID_PROJETO"))
location = str (os.getenv("LOCALIZACAO"))

def generate(conteudo, prompt_instructions):

  # Nesse caso, esta sendo jogado, o texto extraido em string, e o prompt de regras vem de fora.
  # Recebe o conteúdo em String, e o prompt de instruções.
  # Retorna o texto gerado pela IA.
  
  client = genai.Client(
            vertexai=True,
            project=project,
            location=location, 
        )

  conteudo = str(conteudo)
  conteudo = types.Part.from_text(text=conteudo)
  prompt_instructions = str(prompt_instructions)

  model = "gemini-2.5-flash-lite"
  contents = [
    types.Content(
      role="user",
      parts=[
        conteudo
      ]
    ),
  ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 65535,
    system_instruction=[types.Part.from_text(text=prompt_instructions)],
    thinking_config=types.ThinkingConfig(
      thinking_budget=0,
    ),
  )

  result_text = "" # Inicia a String vazia.
  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    if hasattr(chunk, "text"):
      result_text += chunk.text # Concatena o texto recebido ao resultado final.

  return result_text # Retorna o texto em String.