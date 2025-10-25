from PyPDF2 import PdfReader
import re
import pymupdf4llm


def gerar_json_fatias(pdf_partes,tamanho_fatia=200): #Padrão de 200 caracteres.

    #Função que vai gerar o JSON das fatias do PDF.
    #Essa função recebe a lista de partes do PDF, e o numero do ID, que irá ser incrementado.
    #Ela retorna uma lista de dicionarios, onde cada dicionario contem as partes do PDF, e seus dados de origem.

    pdf_partes_fatiado = []

    for item in pdf_partes:
        conteudo_fatiado = fatiar_conteudo(item['conteudo'], tamanho_fatia)
        
        for parte in conteudo_fatiado:
            novo_item = {
                'posicaoFatia': len(pdf_partes_fatiado) + 1,
                'pagina': item['pagina'],
                'conteudo': parte
            }

            pdf_partes_fatiado.append(novo_item)
    
    return pdf_partes_fatiado

def fatiar_conteudo(conteudo, tamanho):
    #Essa função serve para fatiar o conteudo, para que ele possa ser salvo no JSON.
    #Ele recebe o conteudo (O Pdf inteiro), e o tamanho que ele deve ser fatiado.
    #Retorna uma lista com o conteudo fatiado.
    
    partes = []

    while len(conteudo) > tamanho:
        corte = tamanho

        #Essa parte serve para cortar o texto, sem cortar no meio de uma palavra.
        while corte < len(conteudo) and not conteudo[corte].isspace():
            corte += 1
        partes.append(conteudo[:corte].strip())
        
        conteudo = conteudo[corte:].strip() #Remove o texto que foi cortado.
    
    if conteudo:
        partes.append(conteudo)
    
    return partes

def remover_cabecalho(conteudos_paginas, n_palavras=10, threshold=0.5):
    inicios_paginas = []
    
    # Coletar primeiras palavras de cada página
    for item in conteudos_paginas:
        palavras = item['conteudo'].split()
        inicio = palavras[:n_palavras] if len(palavras) >= n_palavras else palavras.copy()
        inicios_paginas.append(inicio)
    
    # Determinar cabeçalho comum
    cabecalho = []
    total_paginas = len(inicios_paginas)
    requerido = max(int(total_paginas * threshold), 1)
    
    # Procurar pelo padrão mais longo que atenda ao threshold
    for k in range(n_palavras, 0, -1):
        frequencia = {}
        for inicio in inicios_paginas:
            if len(inicio) < k:
                continue
            sequencia = tuple(inicio[:k])
            frequencia[sequencia] = frequencia.get(sequencia, 0) + 1
        
        # Verificar se alguma sequência atende o threshold
        for sequencia, count in frequencia.items():
            if count >= requerido:
                cabecalho = list(sequencia)
                break
        if cabecalho:
            break
    
    # Remover o cabeçalho detectado do conteúdo
    if cabecalho:
        for item in conteudos_paginas:
            palavras = item['conteudo'].split()
            if len(palavras) >= len(cabecalho) and palavras[:len(cabecalho)] == cabecalho:
                item['conteudo'] = ' '.join(palavras[len(cabecalho):]).strip()
    
    return conteudos_paginas

def extrair_dados_pdf(nome_arquivo):
    
    with open(nome_arquivo, 'rb') as dados:
        arquivo = PdfReader(dados)
        
        page_list = list(range(len(arquivo.pages))) #Lista com o número de páginas do PDF
        
        md_text = []
        for page_num in page_list:
            page_content = pymupdf4llm.to_markdown(nome_arquivo, pages=[page_num]) # Converte o PDF para Markdown

            page_content = re.sub(r'\s+', ' ', page_content).strip()# Remove espaços em branco extras
            page_content = re.sub(r'\\u[0-9a-fA-F]{4}', '', page_content)  # Remove caracteres Unicode como \u200
            page_content = re.sub(r'[\u202a\u202b\u202c\u202d\u202e\u200e\u200f]', '', page_content)
            
            md_text.append({"pagina": page_num + 1, "conteudo": page_content}) #Preciso atualizar essa parte.


        conteudos = [item["conteudo"] for item in md_text] # Cria uma lista com todos os itens "Conteudo".
        # md_text = remover_cabecalho(md_text, n_palavras=10, threshold=0.5) #Remove o cabeçalho do texto.
        # fatias = gerar_json_fatias(md_text,300)
        
        return conteudos