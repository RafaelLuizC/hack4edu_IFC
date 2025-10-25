import os, json, re, ast
from typing import Any, Optional

def _extract_json_substring(s: str) -> Optional[str]:
    # encontra o primeiro objeto/array JSON aparente e tenta devolver substring balanceada
    starts = [(m.start(), m.group()) for m in re.finditer(r'[\[\{]', s)]
    for start_idx, ch in starts:
        end_ch = ']' if ch == '[' else '}'
        stack = []
        for i in range(start_idx, len(s)):
            if s[i] == ch:
                stack.append(ch)
            elif s[i] == end_ch:
                if stack:
                    stack.pop()
                    if not stack:
                        return s[start_idx:i+1]
        # se não balanceou, tenta até o fim (retorna parcialmente)
        # não retorna aqui para tentar outros starts
    return None

def _remove_trailing_commas(s: str) -> str:
    # remove vírgulas antes de ] ou }
    s = re.sub(r',\s*(?=[}\]])', '', s)
    return s

def _normalize_quotes(s: str) -> str:
    # tenta converter aspas simples em aspas duplas somente em strings literais simples
    # fallback conservador: usa ast.literal_eval quando possível (mais seguro)
    return s.replace('\r', ' ').replace('\t', ' ')

def trata_json_resposta(texto: Any) -> Any:


    if isinstance(texto, (dict, list)):
        return texto

    s = str(texto).strip()

    # tentativa 1: json.loads direto
    try:
        return json.loads(s)
    except Exception:
        pass

    # tentativa 2: ast.literal_eval (aceita singles quotes, True/False, None)
    try:
        parsed = ast.literal_eval(s)
        # transforma para JSON-serializável (converte tuplas em listas)
        return json.loads(json.dumps(parsed, default=str))
    except Exception:
        pass

    # tentativa 3: extrair substring JSON balanceada
    sub = _extract_json_substring(s)
    if sub:
        sub_try = _remove_trailing_commas(_normalize_quotes(sub))
        try:
            return json.loads(sub_try)
        except Exception:
            try:
                parsed = ast.literal_eval(sub_try)
                return json.loads(json.dumps(parsed, default=str))
            except Exception:
                pass

    # tentativa 4: reparar com remoção de vírgulas finais e tentar novamente em todo texto
    try:
        repaired = _remove_trailing_commas(_normalize_quotes(s))
        return json.loads(repaired)
    except Exception:
        pass

    # última tentativa: busca por linhas que parecem JSON e tenta linha a linha
    lines = s.splitlines()
    candidates = []
    for line in lines:
        line = line.strip()
        if line.startswith('{') or line.startswith('['):
            candidates.append(line)
    for c in candidates:
        try:
            return json.loads(_remove_trailing_commas(_normalize_quotes(c)))
        except Exception:
            try:
                parsed = ast.literal_eval(c)
                return json.loads(json.dumps(parsed, default=str))
            except Exception:
                continue

    # se tudo falhar, retorna lista vazia e informa erro (caller pode logar)
    raise ValueError(f"Não foi possível converter a resposta em JSON. Conteúdo (primeiros 200 chars): {s[:200]!r}")

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


def extrair_indices_sumario(arquivo):
    sumario_encontrado = False
    indices = []

    for pagina in range(len(arquivo.pages)):
        texto_pagina = arquivo.pages[pagina].extract_text()
        texto_pagina = texto_pagina.split("\n")
        texto_pagina = texto_pagina[3:-2]
        texto_pagina = " ".join(texto_pagina)

        if "S UMÁRIO" in texto_pagina:  # Por algum motivo, tem um espaço no inicio do texto.
            sumario_encontrado = True

        if sumario_encontrado:  # Se o sumário foi encontrado, começa a capturar os índices
            texto_pagina = texto_pagina.split(" ")

            # Essa parte faz a filtragem dos dados da lista de texto_pagina, para que sejam capturados apenas os índices.
            # Ela não verifica a Pagina, mas somente o que já foi adicionado anteriormente à lista de indices.
            for i in range(len(texto_pagina)):
                texto_indice = []
                if "." in texto_pagina[i]:
                    try:
                        if texto_pagina[i][0].isdigit():
                            num_indice = texto_pagina[i]

                        while not texto_pagina[i].isdigit():
                            texto_indice.append(texto_pagina[i])
                            i += 1
                        if texto_pagina[i].isdigit() and (int(texto_pagina[i].strip()) < len(arquivo.pages)):
                            indices.append({
                                "Numero": num_indice,
                                "Texto": ((" ".join(texto_indice)).replace(num_indice, "")).strip(),
                                "Pagina": int(texto_pagina[i].strip())
                            })
                    except IndexError:
                        break

            # Para de procurar pelo índice quando encontrar a palavra "REFERÊNCIAS"
            if "REFERÊNCIAS" in texto_pagina:
                break

    return indices
