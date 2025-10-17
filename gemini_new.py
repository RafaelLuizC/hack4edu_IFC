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

prompt_ocr = """Você é um assistente especializado em análise de conteúdo educacional e geração de mapas mentais.

Sua tarefa é:
1. Analisar o texto fornecido pelo usuário, que pode conter resumos, listas de exercícios, tópicos de aula ou anotações de professor.  
2. Identificar os **principais temas (tópicos)** e seus **subtemas (subtópicos)** com base na estrutura e no conteúdo.  
3. Eliminar repetições e combinar conteúdos semelhantes.  
4. Criar **sínteses explicativas curtas e objetivas** sobre o que o aluno deve entender ou fazer para resolver questões relacionadas a cada tema ou subtema.  
5. Retornar o resultado **exclusivamente** em formato JSON, na seguinte estrutura:  

```json
[
  {
    "Topico": "NOME DO TÓPICO PRINCIPAL",
    "Conteudo": "Resumo explicativo geral do tópico.",
    "Subtopicos": [
      {
        "Nome": "NOME DO SUBTÓPICO",
        "Conteudo": "Síntese explicativa ou instrução de aprendizado referente a este subtema."
      }
    ]
  }
]

Regras Importantes:

O JSON deve conter apenas tópicos e subtemas únicos (sem repetições).
O campo "Conteudo" deve conter exemplos do professor, de forma clara, direta e útil para estudo ou resolução de exercícios.
Se um tópico não tiver subdivisões, retorne apenas "Topico" e "Conteudo".
Se houver subdivisões claras (ex: fórmulas, propriedades, casos, exemplos), insira-as como "Subtopicos".
Não adicione nenhum texto fora do JSON.
Preserve a clareza e a coerência lógica da hierarquia.
Organize ele de forma que facilite o estudo e a revisão dos conteúdos apresentados no texto original.
"""
# Exemplo de Saída Esperada:

# Saída JSON:
# ```json
# [
#   {
#     "Topico": "Medidas Descritivas",
#     "Conteudo": "Resumem um conjunto de dados por meio de medidas centrais e de dispersão.",
#     "Subtopicos": [
#       {"Nome": "Média", "Conteudo": "Soma dos valores dividida pela quantidade de elementos."},
#       {"Nome": "Mediana", "Conteudo": "Valor central de um conjunto ordenado."},
#       {"Nome": "Moda", "Conteudo": "Valor que mais se repete nos dados."},
#       {"Nome": "Variância", "Conteudo": "Mede o grau de dispersão dos dados em relação à média."},
#       {"Nome": "Desvio Padrão", "Conteudo": "Raiz quadrada da variância, representa a dispersão média."}
#     ]
#   },
#   {
#     "Topico": "Distribuição de Poisson",
#     "Conteudo": "Modela a probabilidade de um número de eventos ocorrer em um intervalo fixo.",
#     "Subtopicos": [
#       {"Nome": "Taxa de Ocorrência (λ)", "Conteudo": "Número médio de eventos em um intervalo."},
#       {"Nome": "Cálculo de Probabilidade", "Conteudo": "Usa a fórmula P(x) = (λ^x * e^-λ) / x!."}
#     ]
#   },
#   {
#     "Topico": "Banco de Dados",
#     "Conteudo": "Ferramentas de manipulação e execução de consultas SQL.",
#     "Subtopicos": [
#       {"Nome": "Views", "Conteudo": "Consultas salvas que se comportam como tabelas virtuais."},
#       {"Nome": "Stored Procedures", "Conteudo": "Blocos de código SQL armazenados no banco para execução automática."}
#     ]
#   }
# ]
# """

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
    correcao_ocr_path = "output/correcao3_ocr_lista1.json"
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

    #texto_perguntas = generate(texto_corrigido, prompt_perguntas)

    #print(texto_perguntas)