from PyPDF2 import PdfReader
import re, sys, os
import pymupdf4llm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #Serve para importar a pasta raiz.
from pdf_parser.extrator_ppc import gerar_json_fatias
from util.prompts import *

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