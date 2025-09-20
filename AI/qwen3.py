from transformers import AutoModelForCausalLM, AutoTokenizer
import time, json, re, sys, os
from llama_cpp import Llama

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #Serve para importar a pasta raiz.

from util.prompts import *
from databases.bd_search import busca_vetores

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

    lista_itens_recuperados = []
    
    print("\nETAPA 1: CLASSIFICAÇÃO")
    nomes_links = format_areas_busca(dicionario_links) #Gera a string com as áreas de busca.
    prompt = analise_pergunta2(nomes_links)

    print (f"Prompt de Análise: {prompt}")
    print (type(prompt), type(mensagens))

    prompt_analise = [prompt, usuario]

    texto_json, pensamento = ia_local(prompt_analise) #Gera o conteudo

    #print(f"JSON Recebido do Modelo: {texto_json}")

    acoes, sucesso = trata_json_resposta(texto_json)  # Tenta converter o JSON

    if not sucesso: #Caso não tenha conseguido converter o JSON.        
        print (f"Ações: {acoes}") #Ações nesse caso é a resposta do modelo.
        mensagem_erro = {"Erro": "Formato inválido na resposta do assistente (esperava uma lista de ações)","Ação":acoes}
        #inserir_logs("error_logs",mensagem_erro) #Insere o log de erro, caso não tenha conseguido converter o JSON.
        
        return acoes, None

    # Garante que 'acoes' seja um dict (caso venha como lista, pega o primeiro elemento)
    if isinstance(acoes, list) and len(acoes) > 0:
        acoes = acoes[0]
    
    elif not isinstance(acoes, dict):
        print(f"Formato inesperado para 'acoes': {acoes}")
        return "Erro: formato inesperado para ações.", None

    acao = acoes.get("acao")

    if acao == "responder_diretamente":
        parametros = acoes.get("parametros", {})
        resposta_direta = parametros.get("texto_resposta", "Desculpe, não tenho uma resposta para isso no momento.")
        return resposta_direta, None

    if acao == "buscar_informacao":
        parametros = acoes.get("parametros", {})
        item = parametros.get("query_de_busca", "")
        area = parametros.get("area_de_busca", "")

        documentos = busca_vetores({"area": area, "busca": item}, 3)

        if not documentos: #Caso nenhum documento tenha sido encontrado.
            #inserir_logs("error_logs", {"Erro": "Nenhum documento encontrado", "Ação": item})
            itens_recuperados_str = "Não foram encontrados itens relacionados à sua consulta."

        else:
            for doc in documentos: #Para cada documento encontrado:
                if doc.get('conteudoPagina'): #Get conteúdo da página.
                                        
                    #Monta a string que irá para a lista de dados recuperados.
                    doc_str = f"Título: {doc.get('tituloPagina', 'N/A')}\nConteúdo: {doc.get('conteudoPagina', '')}" 
                    lista_itens_recuperados.append(doc_str)
                    print (doc_str)


            itens_recuperados_str = "\n\n---\n\n".join(lista_itens_recuperados) #Gera uma string com os itens recuperados. 

        prompt_sintese = prompt_geracao_conteudo_2(str(mensagens),str(mensagens[-1]),itens_recuperados_str) #Gera o prompt de síntese, incluindo os itens recuperados.

        #conteudo = gerar_conteudo_vertex(prompt, mensagens, temperature=0.9) #Gera o conteudo final, baseado na síntese.

        print (type(prompt_sintese), (type(usuario)))

        prompt_sintese = [prompt_sintese, usuario]

        conteudo, pensamento = ia_local(prompt_sintese) #Gera o conteudo final, baseado na síntese.

        print(f"Conteúdo Gerado: {conteudo}")

        return conteudo, None

    if acao == "pedir_esclarecimento":
        parametros = acoes.get("parametros", {})
        pedido_esclarecimento = parametros.get("texto_resposta", "Desculpe, não entendi sua pergunta. Poderia esclarecer?")
        return pedido_esclarecimento, None

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
        enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
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

    while True:
        mensagem_usuario = input("Digite sua mensagem: ")
        start_time = time.time()

        usuario = ({"role": "user", "content": mensagem_usuario})
        mensagens = [usuario]
        resposta, itens_recuperados = pipeline_qwen(mensagens)

        print (f"\nResposta: {resposta}")
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
