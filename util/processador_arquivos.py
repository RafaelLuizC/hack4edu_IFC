import json
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import re
import os

from processing.pdf import extrair_dados_pdf
from processing.ocr import extrair_dados_ocr

#Esse codigo recebe um arquivo Json, que contem links para PDFs, e baixa o conteudo de cada PDF, e salva em um novo Json com os dados do PDF dentro dele.

#Para que eu possa fazer esse codigo funcionar da maneira como é esperada eu vou precisar fazer as seguintes modificações.
#1. Preciso que com base nos dados do Banco de dados Mongo, eu possa fazer uma varredura dos dados de lá, e por lá, conseguir fazer o download dos PDFs.

#Aqui vai ter que mudar para receber os dados do banco de dados.

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

def processar_arquivo(link):
    
    #Essa função baixa o arquivo, e salva ele em um arquivo temporario, para que eu possa fazer a leitura do conteudo dele.
    #O objetivo é que essa função baixe qualquer arquivo, verifique a extensão dele, e faça a leitura do conteudo dele.
    
    lista_extensoes = ["pdf"] #, "docx", "doc", "txt", "xlsx", "xls", "pptx", "ppt" #Proximas extensões a serem adicionadas.

    extensao = verifica_extensao(link) #Verifica a extensão do arquivo.

    if extensao not in lista_extensoes: # Verifica se a extensão é suportada
        
        print(f"Extensão {extensao} não suportada.")
        
        return None #Adiciona um retorno para evitar erro caso a extensão não seja suportada.

    try:
        response = requests.get(link)
        response.raise_for_status()
        arquivo = response.content
        nome_arquivo_temporario = f'temp.{extensao}'
        #Vou usar a mesma logica aqui, mas o programa irá ao inves de salvar como "temp.pdf", ele irá salvar esse pdf em outra pasta.
        #O nome do arquivo, será o mesmo nome do link, mas com a extensão .pdf.
        
        with open(nome_arquivo_temporario, 'wb') as arquivo_temporario:
            arquivo_temporario.write(arquivo) 
        
        #Essa parte do codigo, serve para abrir o documento que acabou de ser salvo, e fazer a leitura do conteudo dele.
        with open(nome_arquivo_temporario, 'rb') as arquivo_temporario:

            if extensao == "pdf":
                arquivo_pdf = PdfReader(arquivo_temporario)
                status_pdf = check_pdf(arquivo_pdf) #Verifica se o PDF está quebrado ou não.
                
                if status_pdf == "quebrado" or status_pdf == "imagem":
                    conteudo = extrair_dados_ocr(nome_arquivo_temporario) #Faz a leitura do PDF quebrado, e salva o conteudo em um arquivo JSON.
                
                elif status_pdf == "texto":
                    conteudo = extrair_dados_pdf(nome_arquivo_temporario)
                
                return conteudo
                
            #elif extensao in ["docx", "doc"]:
            #    pass

        os.remove(nome_arquivo_temporario)   

    except requests.RequestException as e:
        print(f"Erro ao baixar o PDF: {e}")
        return None

if __name__ == '__main__':

    lista_fatias = processar_arquivo("http://www.camboriu.ifc.edu.br/editais/wp-content/uploads/sites/15/2025/04/Edital_25_de_2025_-_Professor_Conteudista_Vagas_No_Preenchidas.pdf") #Essa função vai baixar o arquivo, e depois fazer a leitura do conteudo dele.

    for item in lista_fatias:
       print (f'Conteudo da Fatia:{item}\n')

    #print (lista_fatias)

    with open("out-malalalalal.md", "r", encoding="utf-8") as output: #Só pra quebrar o programa.
        pass
    #Ok, precisamos começar a organizar esse sistema, esta bem bagunçado.
    #Para isso, vou separar esse documento em diversas funções, a primeira, terá o objetivo de determinar qual é a extensão do arquivo.

    #O Objetivo é que ele faça isso a partir do Banco de Dados, mas, irei utilizar o arquivo JSON por enquanto.

    #Com base no arquivo data, eu vou criar um novo Json, que irá conter as mesmas informações do arquivo data
    #Mas com a adição de cada PDF conter tambem, o seu conteudo em texto.
    # Caminho para a pasta contendo os arquivos JSON

    # Lista todos os arquivos JSON na pasta
    # json_files = [os.path.join('json_novos', f) for f in os.listdir('json_novos') if f.endswith(".json")]

    # # Carrega todos os arquivos JSON em uma lista
    # data = []
    # for json_file in json_files:
    #     with open(json_file, encoding='utf-8') as f:
    #         data = json.load(f)

    #     lista_arquivos = []

    #     for i in data:
    #         for item in i.get("links", []):
    #             link = item.get("href", "") #Usando GET para evitar erro caso o "href" e "links" não exista.

    #             #Lista de extensões validas:
    #             extensao = verifica_extensao(link)                

    #             if extensao in lista_extensoes:
    #                 processar_arquivo(link,extensao)


    #     with open('data2_modified.json', 'w', encoding='utf-8') as f:
    #         json.dump(data, f, ensure_ascii=False, indent=4)
            
    #     pass

#A Parte abaixo serve para encontrar os nomes e numeros dos editais, mas ainda estou trabalhando nisso.
# contador = 0
# not_found_count = 0

# for item in data:
#     contador += 1
#     conteudo = item["conteudo"]
#     found = False
#     for symbol in ["º", "°", "N°", "No", "Nº"]:
#         if symbol in conteudo:
#             index = conteudo.index(symbol)
#             start = max(0, index - 10)
#             end = min(len(conteudo), index + len(symbol) + 10)
#             print(conteudo[start:end])
#             found = True
#             break
#     if not found:
#         print("Não encontrado")
#         not_found_count += 1

# print(f"Total de não encontrados: {not_found_count}")