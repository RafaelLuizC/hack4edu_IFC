from google import genai
from google.genai import types
import base64
import os, re

import json, os, dotenv, time, sys
from util.helpers import *
from util.prompts import *
#from AI.qwen3 import ia_local
from pdf_parser.pdf import extrair_dados_pdf
from databases.bd_utils import *

dotenv.load_dotenv()
project = str (os.getenv("ID_PROJETO"))
location = str (os.getenv("LOCALIZACAO"))

perfil_do_usuario = """Rafael Luiz, tem 26 anos e quer aprender mais sobre Estatistica e Probabilidade para se sair bem em suas aulas no IFC, gosta de bicicletas, jogos de tabuleiro e tecnologia. Prefere aprender por meio de exemplos práticos."""

def trata_json_resposta(string_json):

    if isinstance(string_json, dict):  # Se já é dict, retorna como lista
        print ("Ele foi tratado como dict naturalmente.")

        return [string_json]

    try:
        # Remove possíveis blocos de markdown e espaços extras
        clean_json_str = str(string_json).strip()
        clean_json_str = re.sub(r"^```json|```$", "", clean_json_str, flags=re.MULTILINE).strip()

        # Tenta encontrar o primeiro objeto/lista JSON válido na string
        match = re.search(r"(\[.*\]|\{.*\})", clean_json_str, re.DOTALL)

        print ("Foi necessario a transformação da String.")

        if match:
            clean_json_str = match.group(0)

        #print(f"String JSON limpa: {clean_json_str}")

        acoes = json.loads(clean_json_str)

        return acoes

    except Exception as e:
        print(f"Erro ao converter resposta em JSON:\n{string_json}\nDetalhe: {e}")
        return string_json


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

def pipeline_tarefas(texto_referencia):

  os.makedirs("output", exist_ok=True)
  correcao_ocr_path = "output/correcao1_ocr_lista3.json"

  print ("Lendo texto do PDF...")
  texto_extraido = extrair_dados_pdf(texto_referencia)
  texto_extraido = ' '.join(texto_extraido)

  texto_corrigido = generate(texto_extraido, prompt_parser())

  texto_corrigido = trata_json_resposta(texto_corrigido)

  #Salva o texto corrigido no banco de dados.
  for item in texto_corrigido:
      #A função se chama inserir_logs, pq peguei de outro codigo.
      inserir_logs('atividades_parser', item)

  item = texto_corrigido[0] #Pega o primeiro item da lista, mas isso é porque não fiz um algoritmo para isso ainda.

  print (f"O item 0 é: {item}")

  # --- Gerar Trilha de Aprendizado ---

  print ("\nGerando trilha de aprendizado...\n")

  trilha_aprendizado = generate(texto_corrigido, prompt_trilha().replace("[SUBSTITUIR-PERFIL-USUARIO]", perfil_do_usuario).replace("[SUBSTITUIR-TEMA]", item["Topico"]))
  trilha_aprendizado = trata_json_resposta(trilha_aprendizado)

  #Salva a trilha de aprendizado no banco de dados.
  for item in trilha_aprendizado: #Para cada item na trilha de aprendizado.
      inserir_logs('trilhas_aprendizado', item)

  # --- Gerar Atividades Detalhadas ---

  print ("\nGerando atividades detalhadas...\n")

  atividades = generate(str(trilha_aprendizado), prompt_atividades())

  atividades = trata_json_resposta(atividades)

  #Salva as atividades detalhadas no banco de dados.
  for atividade in atividades:
      inserir_logs('atividades_detalhadas', atividade)

if __name__ == "__main__":

  # PDF Path é o caminho do PDF que será processado.
  pdf_path = "pdf_sample/Lista1Estatstica.pdf"
  
  # Ele ta salvando no MongoDB, para salvar, é necessario verificar a pasta databases/bd_utils.py.
  # Nele tem a função inserir_logs, que salva os dados no MongoDB, se quiser modificar os dados de conexão, é só alterar lá.

  #Não retorna nada, apenas executa a pipeline de tarefas.
  pipeline_tarefas(pdf_path) #
