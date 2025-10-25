import os, json, re, ast
from typing import Any, Optional

def parse_json_string(string: str) -> Optional[str]:
    # encontra o primeiro objeto/array JSON aparente e tenta devolver substring balanceada
    
    starts = [(m.start(), m.group()) for m in re.finditer(r'[\[\{]', string)] # Encontra indices de abertura. 
    for start_idx, ch in starts:
        
        end_ch = ']' if ch == '[' else '}' # Caracteres de fechamento correspondentes
        stack = [] # Pilha...
        
        for i in range(start_idx, len(string)): # Percorre a string a partir do caractere de abertura

            if string[i] == ch: # Se encontrou caractere de abertura
                stack.append(ch)
            
            elif string[i] == end_ch: # Se encontrou caractere de fechamento
                if stack: # Se a pilha não estiver vazia, desempilha.
                    stack.pop()
    
                    if not stack: # Se a pilha estiver vazia, significa que encontramos correspondência.
                        return string[start_idx:i+1]
    
    # Não retorna aqui para tentar outros starts
    return None

def remove_virgulas_parenteses(string: str) -> str:
    # remove vírgulas antes de ] ou }
    
    string = re.sub(r',\s*(?=[}\]])', '', string)
    return string

def normaliza_aspas(string: str) -> str:
    # tenta converter aspas simples em aspas duplas somente em strings literais simples
    # fallback conservador: usa ast.literal_eval quando possível (mais seguro)
    
    return string.replace('\r', ' ').replace('\t', ' ')

def trata_json_resposta(texto: Any) -> Any:
    # Nem sempre o modelo formata corretamente a resposta em JSON, então essa função tenta consertar isso.
    # Essa função tenta converter uma resposta de texto em JSON.
    # Tenta ser uma função bem robusta, ela possui 4 métodos diferentes para tentar converter o texto em JSON.
    # Se todos os métodos falharem, ela retorna erro.

    if isinstance(texto, (dict, list)): # Se já for dict ou list, retorna como está.
        return texto

    string_busca = str(texto).strip() # Garante que é uma string, e remove espaços em branco desnecessários.

    # Simplesmente tenta json.loads primeiro, vai que né. 
    try:
        return json.loads(string_busca)
    except Exception:
        pass

    # Segunda tentativa: tenta usar ast.literal_eval para interpretar a string.
    try:
        parsed = ast.literal_eval(string_busca)
        # transforma para JSON-serializável (converte tuplas em listas)
        return json.loads(json.dumps(parsed, default=str))
    
    except Exception:
        pass

    # Terceira tentativa: tenta extrair substring JSON aparente e processar, usa normalização de aspas e remoção de vírgulas.
    sub = parse_json_string(string_busca)
    if sub:
        sub_try = remove_virgulas_parenteses(normaliza_aspas(sub))
        
        try:
            return json.loads(sub_try) # tenta com json.loads primeiro.
        
        except Exception:
            try: # tenta com literal_eval se json.loads falhar.
                parsed = ast.literal_eval(sub_try)
                return json.loads(json.dumps(parsed, default=str))
            
            except Exception:
                pass # Se falhar, continua para a próxima tentativa.

    # Quarta tentativa: Tenta usando normalização de aspas e remoção de vírgulas.
    try:
        repaired = remove_virgulas_parenteses(normaliza_aspas(string_busca))
        return json.loads(repaired)
    except Exception:
        pass

    # Quinta tentativa: busca linhas que parecem JSON e tenta linha a linha.
    # Esta na ultima posição porque é a menos eficiente. Muito menos.
    lines = string_busca.splitlines() # Divide em linhas.
    candidates = []
    
    for line in lines: # Para cada linha, remove espaços em branco desnecessários.
        line = line.strip()
        
        if line.startswith('{') or line.startswith('['): # Se a linha começar com { ou [, considera como candidata.
            candidates.append(line)
    
    for c in candidates: # Para cada candidata, tenta converter em JSON.
        try:
            return json.loads(remove_virgulas_parenteses(normaliza_aspas(c))) # Tenta com json.loads primeiro.
        except Exception:
            try:
                parsed = ast.literal_eval(c) # Tenta com literal_eval se json.loads falhar.
                return json.loads(json.dumps(parsed, default=str)) 
            except Exception:
                continue

    # Se tudo falhar, retorna lista vazia e informa erro. Retorna 100 primeiros chars para debug.
    raise ValueError(f"Não foi possível converter a resposta em JSON. Conteúdo (primeiros 100 chars): {string_busca [:100]!r}")

def separador_item(linha,palavra_inicial,palavra_final):
    
    #Ela recebe a linha, um identificador inicial, um final, e remove oque possui entre eles.
    
    item = linha

    i = item.find(palavra_inicial) #Procura a primeira palavra.
    x = item.find(palavra_final,i+1) #Procura a segunda palavra.

    if palavra_inicial == "Primeira": #Se estiver procurando a primeira palavra, ele pega do inicio da String.
        item = item[:x]
        return item

    if palavra_final == "Ultima" or i == -1: #Se estiver procurando a ultima palavra, ele pega do final da String.
        item = item[i:]
        return item

    item = item[i:x] #Se não, ele pega do inicio da primeira palavra até o final da segunda palavra.

    return item #Retorna o item.


def check_pdf(arquivo_pdf, min_palavras_por_pagina=20):

    # Essa função verifica se o PDF está quebrado ou não, e retorna "quebrado", "imagem" ou "texto".
    #Ela recebe o arquivo PDF e o número mínimo de palavras por página como parâmetros.
    #Caso ele não consiga encontrar texto legivel, ele vai considerar que o PDF está quebrado.

    for page in arquivo_pdf.pages:
        texto = page.extract_text() or ""
        palavras = re.findall(r'\b\w+\b', texto)
        
        if not palavras: 
            return "quebrado" # Se não houver palavras, considera "quebrado" 
        
        palavras_numericas = [palavra for palavra in palavras if palavra.isdigit()] #Verifica se a "palavra" é um número.
        proporcao_numerica = len(palavras_numericas) / len(palavras)
        
        if proporcao_numerica > 0.75:
            return "quebrado"  # Se mais de 75% das palavras forem números, considera "quebrado"
        
        if 0 < len(palavras) < min_palavras_por_pagina:
            return "quebrado"  # Se houver texto, mas insuficiente, considera "quebrado"
        
        if len(palavras) >= min_palavras_por_pagina:
            return "texto"  # Se houver texto suficiente, considera "texto"
    
    return "imagem"

def verifica_extensao(link):
    
    extensao = link.split(".")[-1] #Pega a extensão do link, a partir do ponto final.

    if not extensao or len(extensao) > 5:  # Caso o link não tenha extensão, a verificação de comprimento, serve para evitar links com extensões muito longas.
        extensao = "nulo"

    return extensao
