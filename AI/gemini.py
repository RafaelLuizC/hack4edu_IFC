
import json, os, dotenv, time, sys
#from databases.bd_search import busca_vetores, inserir_logs
from google import genai
from google.genai import types
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #Serve para importar a pasta raiz.
from util.helpers import *
from util.prompts import *
#from AI.qwen3 import ia_local
from processing.pdf import extrair_dados_pdf

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
            max_output_tokens=60000,
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

    mensagens_lista = [prompt] + mensagens
    # Garante que o primeiro item seja um dicionário com a chave 'content'
    if not mensagens_lista:
        return None, []

    primeiro = mensagens_lista[0]
    if isinstance(primeiro, dict) and 'content' in primeiro:
        system_instruction = primeiro['content']
    elif isinstance(primeiro, str):
        system_instruction = primeiro
    else:
        system_instruction = str(primeiro)

    vertex_contents = []
    # Começa do segundo item, já que o primeiro é a instrução do sistema
    for msg in mensagens_lista[1:]:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = str(msg.get("content", ""))
        else:
            role = "user"
            content = str(msg)

        if role.lower() in ["assistant", "system"]:
            role = "model"

        vertex_contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=content)]
            )
        )
    return system_instruction, vertex_contents

def gerar_perguntas_vertex(texto_referencia):

    fatias = extrair_dados_pdf(texto_referencia)

    fatias = [{"role": "system", "content": fatias}]

    prompt = prompt_correcao_ocr()

    system_instruction, vertex_contents = formatar_mensagens_para_vertex(fatias, prompt)

    print (f"Informações do Sistema: {system_instruction}")
    print (f"Conteúdos para o Vertex: {vertex_contents}")

    if not vertex_contents:
        return "Erro: Nenhuma mensagem válida para processar."

    resposta = gerar_conteudo_vertex(system_instruction, vertex_contents, temperature=0.7, model="gemini-2.5-flash-lite")

    #acoes, sucesso = trata_json_resposta(resposta)

    #if not sucesso:
    #    return f"Erro ao interpretar a resposta do modelo: {acoes}"

    return resposta


if __name__ == "__main__":

    texto_referencia = "pdf_sample/LISTA_1__MEDIDAS_DESCRITIVAS___Estatstica.pdf"
    resultado = gerar_perguntas_vertex(texto_referencia)

    print("Resultado Final:")
    print(resultado)
