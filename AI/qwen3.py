from transformers import AutoModelForCausalLM, AutoTokenizer
import time, json, re, sys, os
from llama_cpp import Llama

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #Serve para importar a pasta raiz.

from util.prompts import *
from processing.pdf import extrair_dados_pdf

dicionario_links = [{"link": "https://www.camboriu.ifc.edu.br/noticias/category/noticias/","pagina_indice": "True","nome_link":"Noticias"},
                     {"link": "https://www.camboriu.ifc.edu.br/editais/","pagina_indice": "True","nome_link":"Editais"},
                     {"link": "https://www.camboriu.ifc.edu.br/cursos-tecnicos/integrado-ao-ensino-medio/informatica/","pagina_indice": "False","nome_link":"Curso_Informatica"},
                     {"link": "https://www.camboriu.ifc.edu.br/pos-graduacao/pos-graduacao-em-educacao/","pagina_indice": "False","nome_link":"Pós-graduação em Educação"},
                     {"link": "https://www.camboriu.ifc.edu.br/pos-graduacao/pos-graduacao-em-gestao-e-negocios/","pagina_indice": "False","nome_link":"Pós-Graduação em Gestão e Negócios"},
                     {"link": "https://www.camboriu.ifc.edu.br/bacharelado-em-agronomia-2/","pagina_indice": "False","nome_link":"Bacharelado em Agronomia"},
                     {"link": "https://www.camboriu.ifc.edu.br/cursos-superiores/bacharelado-em-sistemas-de-informacao/","pagina_indice": "False","nome_link":"Bacharelado em Sistemas de Informação"},
                     {"link": "https://www.camboriu.ifc.edu.br/cursos-superiores/licenciatura-em-matematica/","pagina_indice": "False","nome_link":"Licenciatura em Matemática"}]

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


def format_areas_busca(areas_busca):
    result = []
    for item in areas_busca:
        nome = item["nome_link"]
        tipo = "Curso" if item["pagina_indice"] == "False" else item["nome_link"]
        result.append(f"- **Nome da Área:**{nome}**, **Tipo:** {tipo}")
    return "\n".join(result)

def convert_messages_to_qwen3(messages):
    template = ""
    role_map = {"system": "system", "user": "user", "assistant": "assistant"}
    for msg in messages:
        role = role_map.get(msg.get("role"), "user")
        content = msg.get("content", "")
        template += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    print (template)
    return template

def pipeline_qwen(mensagens):

    pass

def ia_local(messages):

    #Carrega o Tokenizer e o modelo.
    model_name = "Qwen/Qwen3-0.6B"
    #model_name = "Qwen/Qwen3-8B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False # Switches between thinking and non-thinking modes. Default is True.
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # conduct text completion
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    return content, thinking_content

def ia_local_quant(messages, model_path="modelo\Qwen3-0.6B-UD-Q8_K_XL.gguf"):
    # Carrega o modelo GGUF
    llm = Llama(
        model_path=model_path,
        n_ctx=40960,           # Contexto grande para pensar
        n_threads=4,
        n_gpu_layers=0,        # Ajuste se tiver GPU
        verbose=False
    )
    
    chat_template = ""

    # Cria o template de chat.    
    for message in messages:
        role = message["role"]
        content = message["content"]
        
        if role == "system":
            chat_template += f"<|im_start|>system\n{content}<|im_end|>\n"
        elif role == "user":
            chat_template += f"<|im_start|>user\n{content}<|im_end|>\n"
        elif role == "assistant":
            chat_template += f"<|im_start|>assistant\n{content}<|im_end|>\n"
    
    chat_template += "<|im_start|>assistant\n"
    
    # Gera a resposta
    output = llm(
        chat_template,
        max_tokens=32768,
#        stop=["###", "\n\n"],
        echo=False,
        temperature=0.7
    )
    print (f"Essa é o output cru: {output}")
    response_text = output['choices'][0]['text'].strip()
    thinking_content = ""
    content = response_text

    # Verifica se há conteúdo de thinking (tags </think>)
    if "</think>" in response_text:
        parts = response_text.split("</think>", 1)
        thinking_content = parts[0].replace("<think>", "").strip()
        content = parts[1].strip() if len(parts) > 1 else ""

    print(f"Essa é a resposta: {content}")
    print(f"Esse é o parte de pensamento: {thinking_content}")

    return content, thinking_content

if __name__ == "__main__":

    start_time = time.time()
    texto_referencia = "pdf_sample/LISTA_1__MEDIDAS_DESCRITIVAS___Estatstica.pdf"

    fatias = extrair_dados_pdf(texto_referencia)

    prompt = prompt_correcao_ocr()

    fatias = [{"role": "system", "content": fatias}, prompt]

    resultado = ia_local(texto_referencia)

    print("Resultado Final:")
    print(resultado)
    end_time = time.time()
    print(f"Tempo decorrido: {(end_time - start_time) / 60:.2f} minutos")

    #   prompt = analise_perguntas("Cães Guias")

        #prompt = {"role": "system", "content": "Você é um assistente útil, prestativo e amigável. Responda de forma clara e objetiva."}

        # links = """MATEMATICA","FISICA","QUIMICA"""

        # prompt = analise_pergunta2(links)

        # mensagens = [prompt, usuario]
        # #mensagens = convert_messages_to_qwen3(mensagens)

        # print (mensagens)

        # resposta, pensamentos = chat_ia_local(mensagens)
        
        # print(f"\nResposta: {resposta}")
