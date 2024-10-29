import os
import pandas as pd
from datetime import datetime

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
