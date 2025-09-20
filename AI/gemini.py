import json, os, dotenv, time

from util.helpers import *
#from databases.bd_search import busca_vetores, inserir_logs
from util.prompts import *
from google import genai
from google.genai import types
import re

from AI.qwen3 import ia_local

dotenv.load_dotenv()
id_projeto = str (os.getenv("ID_PROJETO"))
servidor = str (os.getenv("LOCALIZACAO"))


def format_areas_busca(areas_busca):
    result = []
    for item in areas_busca:
        nome = item["nome_link"]
        tipo = "Curso" if item["pagina_indice"] == "False" else item["nome_link"]
        result.append(f"- **Nome da Área:**{nome}**, **Tipo:** {tipo}")
    return "\n".join(result)

def trata_json_resposta(string_json):

    if isinstance(string_json, dict):  # Se já é dict, retorna como lista
        print ("Ele foi tratado como dict naturalmente.")

        return [string_json], True

    try:
        # Remove possíveis blocos de markdown e espaços extras
        clean_json_str = str(string_json).strip()
        clean_json_str = re.sub(r"^```json|```$", "", clean_json_str, flags=re.MULTILINE).strip()

        # Tenta encontrar o primeiro objeto/lista JSON válido na string
        match = re.search(r"(\[.*\]|\{.*\})", clean_json_str, re.DOTALL)

        print ("Foi necessario a transformação da String.")

        if match:
            clean_json_str = match.group(0)

        print(f"String JSON limpa: {clean_json_str}")

        acoes = json.loads(clean_json_str)

        return acoes, True

    except Exception as e:
        print(f"Erro ao converter resposta em JSON:\n{string_json}\nDetalhe: {e}")
        return string_json, False

def gerar_conteudo_vertex(system_instruction_text, contents_list, temperature=1.0, project=id_projeto, location=servidor, model="gemini-2.5-flash-lite"):

    start_time = time.time()

    try:
        client = genai.Client(
            vertexai=True,
            project=project,
            location=location, 
        )

        generate_content_config = types.GenerateContentConfig(
            temperature=temperature, 
            max_output_tokens=8192,
            system_instruction=[types.Part.from_text(text=system_instruction_text)], #Ok, aqui ele recebe a parte das instruções.
        )

        # Usando a chamada síncrona para obter a resposta completa de uma vez
        response = client.models.generate_content(
            model=model,
            contents=contents_list, #Aqui ele recebe a lista de conteúdos, ou mensagens antigas.
            config=generate_content_config,
        )

    except Exception as e:
        tempo_execucao = f"({(time.time() - start_time):.1f}s)" # Tempo total de execução da busca. #Talvez não seja a melhor forma.
        print(f"ERRO ao chamar a API do Vertex AI: {e}")
        
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_instruction_text": system_instruction_text,
            "contents_list": json.dumps(contents_list, default=lambda o: o.__dict__),
            "temperature": temperature,
            "model": model,
            "response_text": response.text,
            "duration": tempo_execucao,
            "success": False,
            "error_message": e
        }
        
        return f"Ocorreu um erro ao comunicar com o modelo: {e}"

    tempo_execucao = f"({(time.time() - start_time):.1f}s)" # Tempo total de execução da busca.

    log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_instruction_text": system_instruction_text[:200],
            "contents_list": json.dumps(contents_list, default=lambda o: o.__dict__),
            "temperature": temperature,
            "model": model,
            "response_text": response.text,
            "duration": tempo_execucao,
            "success": True,
            "error_message": None
    }

    return response.text

def formatar_mensagens_para_vertex(mensagens, prompt):

    mensagens_lista = [prompt] + mensagens #Aqui recebe o prompt de classificação + as mensagens?
    #Essa função recebe uma lista, ela assume que o primeiro item dela são as instruções do sistema.
    #E as seguintes são as mensagens trocadas entre o usuario e o assistente.
    #Ou seja, o papel dela é receber uma lista de mensagens e transformar em um texto para chamar a API do Gemini.

    #Segundo oque o Gemini me respondeu, eu vou precisar adicionar o contexto ao RAG.

    if not mensagens_lista:
        return None, []

    system_instruction = mensagens_lista[0]['content']
    vertex_contents = []
    
    # Começa do segundo item, já que o primeiro é a instrução do sistema
    for msg in mensagens_lista[1:]:
        role = msg.get("role", "user") #Aqui eu estou informando que o papel da mensagem é "user" por padrão.

        if role.lower() in ["assistant", "system"]: #E que "assistant" ou "system" estão sendo usados.
            role = "model"
            
        vertex_contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=str(msg.get("content", "")))]
            )
        )
    return system_instruction, vertex_contents

def gerar_perguntas_vertex(texto_referencia):
    prompt = prompt_geracao_perguntas(texto_referencia)

    system_instruction, vertex_contents = formatar_mensagens_para_vertex(prompt, prompt)

    if not vertex_contents:
        return "Erro: Nenhuma mensagem válida para processar."

    resposta = gerar_conteudo_vertex(system_instruction, vertex_contents, temperature=0.7, model="gemini-2.5-flash-lite")

    #acoes, sucesso = trata_json_resposta(resposta)

    #if not sucesso:
    #    return f"Erro ao interpretar a resposta do modelo: {acoes}"

    return resposta