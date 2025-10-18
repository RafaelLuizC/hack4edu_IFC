from PyPDF2 import PdfReader
import os
import json
import re

from util.helpers import *

def ler_pdf(nome_arquivo,nome_saida='pdf_slices.json',curso='BSI'):

    #Depois posso mudar essa função para se torne a _main_, e receber o nome do arquivo como argumento.

    dados = open(nome_arquivo, 'rb')
    arquivo = PdfReader(dados)
    indices = extrair_indices_sumario(arquivo)

    pdf_unido = unir_pdf(arquivo,indices)

    #Preciso adicionar o Nome do arquivo, e o tipo de informação que estou salvando.

    pdf_partes, paginas_dados_materias = separador_indices(pdf_unido,indices) 
    lista_materias = separador_materias_legado(arquivo,indices)
    strings_dados_materias = unir_elementos_materias(lista_materias,paginas_dados_materias)
    lista_info_materias = classificador_dados_materias(strings_dados_materias)

    materias_completas = gerar_json_materias(lista_materias, lista_info_materias,nome_arquivo,curso)
    pdf_partes_fatiado= gerar_json_fatias(pdf_partes,nome_arquivo,curso)

    itens_unidos = materias_completas + pdf_partes_fatiado

    with open(nome_saida, 'w', encoding='utf-8') as f:
        json.dump(itens_unidos, f, ensure_ascii=False, indent=4)

def extrair_indices_sumario(arquivo):

    #Essa função serve para encontrar o sumário do PDF, e capturar os índices.
    #Ela retorna uma lista de dicionários, onde cada dicionário contém o número do índice, o texto do índice e a página onde ele se encontra.
    #Formato: [{"Numero": "1.1", "Texto": "Introdução", "Pagina": 1}, ...]

    sumario_encontrado = False
    indices = []

    for pagina in range(len(arquivo.pages)):
        texto_pagina = arquivo.pages[pagina].extract_text()
        texto_pagina = texto_pagina.split("\n")
        texto_pagina = texto_pagina[3:-2]
        texto_pagina = " ".join(texto_pagina).upper()

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

def separador_indices(pdf_unido,indices):


    #Essa função recebe uma string unica do PDF, e os indices, e separa o PDF em partes, onde cada parte é um indice.
    #Ela retorna uma lista de partes do PDF, separados com base no indice.
    #Formato: [{"Indice": "1.1", "Texto": "String", "Pagina": 1, "Conteudo": "String"}, ...]

    lista_paginas_materias = [] #Lista com as paginas que contem as materias. #Devo mudar o nome dessa Variavel para algo mais descritivo.

    pdf_partes = [] #Lista que vai conter as partes do PDF, separadas com base no indice.

    for i in range(len(indices)):#Para cada item do Indice.
        try: 
            conteudo_intervalo = separador_item(pdf_unido,indices[i]['Numero'],indices[i+1]['Numero']) #Separa a parte do texto que esta entre os indices.
            pdf_unido = pdf_unido.replace(conteudo_intervalo, "", 1)  # Remove o intervalo

        #O Except é para quando ele chegar no ultimo item do indice, e não tiver um proximo item, ele deve procurar até as referencias.
        except IndexError: 
            conteudo_intervalo = separador_item(pdf_unido,indices[i]['Numero'],"REFERÊNCIAS")
            pdf_unido = pdf_unido.replace(conteudo_intervalo, "", 1)  # Remove o intervalo de pdf_unido

        #Pula esse item.
        if indices[i]['Texto'] == "COMPONENTES CURRICULARES OBRIGATÓRIOS":
            continue
        
        #Se o texto do indice for muito pequeno, ele pula.
        if len(indices[i]['Texto']) > 2:

            #Esses itens contem as informações das materias, e serão adicionados depois.
            if indices[i]['Texto'] == "MATRIZ CURRICULAR DOS COMPONENTES CURRICULARES OPTATIVOS" or indices[i]['Texto'] == "MATRIZ CURRICULAR":
                lista_paginas_materias.append(conteudo_intervalo) #Lista de Paginas com os componentes Optativos.
                continue

            #Adiciona o indice 
            pdf_partes.append({
                "Indice": indices[i]['Numero'],
                "Texto": indices[i]['Texto'],
                "Pagina": indices[i]['Pagina'],
                "Conteudo": conteudo_intervalo
            })

    return pdf_partes , lista_paginas_materias

def separador_materias_legado(arquivo,indices):

    #Essa codigo foi desenvolvido anteriormente, ele funciona separando as materias diretamente do PDF, e não com base no indice, por esse motivo ele funciona melhor para pegar as materias.
    #Mas ele não é tão bom pegando as informações do PDF e as informações de paginas corretas, por isso, esta servindo apenas para a parte de materias.
    #Não é o codigo mais otimizado, mas funciona. Ainda não coloquei a função formata_pagina, que remove o cabeçalho e o rodapé, mas ela deve ser adicionada.

    data_ppc = []

    for i, indice in enumerate(indices):
        
        texto_pagina = arquivo.pages[indice['Pagina']-1].extract_text()
        texto_pagina = texto_pagina.split("\n") 
        texto_pagina = texto_pagina[3:-2]
        texto_pagina = " ".join(texto_pagina)
        
        conteudo_intervalo = [texto_pagina]
        
        # Verifica se há um próximo índice
        if i + 1 < len(indices):
            proximo_indice = indices[i + 1]
            
            # Captura o intervalo até a próxima página marcada no PDF
            for pagina in range(indice['Pagina'], proximo_indice['Pagina']):
                texto_pagina = arquivo.pages[pagina].extract_text()
                texto_pagina = texto_pagina.split("\n")
                texto_pagina = texto_pagina[3:-2] # Remove cabeçalho e rodapé
                texto_pagina = " ".join(texto_pagina)
                
                if "REFERÊNCIAS" in texto_pagina:
                    break
                conteudo_intervalo.append(texto_pagina)
            
            # Se a próxima página for a mesma, usa a função separador_item
            if indice['Pagina'] == proximo_indice['Pagina']:
                texto_pagina = arquivo.pages[indice['Pagina'] - 1].extract_text()
                texto_pagina = texto_pagina.split("\n")
                texto_pagina = texto_pagina[3:-2] # Remove cabeçalho e rodapé
                texto_pagina = " ".join(texto_pagina)
                conteudo_separado = separador_item(texto_pagina, indice['Texto'], proximo_indice['Texto'])
                if len(conteudo_separado) > 2:
                    conteudo_intervalo = conteudo_separado
        else:
            # Captura até o final do documento
            for pagina in range(indice['Pagina']+1, len(arquivo.pages)):
                texto_pagina = arquivo.pages[pagina].extract_text()
                texto_pagina = texto_pagina.split("\n")
                texto_pagina = texto_pagina[3:-2] # Remove cabeçalho e rodapé
                texto_pagina = " ".join(texto_pagina)
                conteudo_intervalo.append(texto_pagina)
                if "CONSIDERAÇÕES FINAIS" in texto_pagina:
                    break
        conteudo_intervalo = " ".join(conteudo_intervalo)

        if "SEMESTRE" in conteudo_intervalo:
            data_ppc.extend(separador_materias(conteudo_intervalo))

    return data_ppc

def unir_pdf(arquivo,indices):

    #Essa função serve para unir o PDF em uma unica string.
    #Ela recebe o arquivo, e retorna uma string unica com todo o texto do PDF.

    pdf_unido = [] #Lista que vai conter o texto unido do PDF.
    for pagina in range(len(arquivo.pages)):
        
        #Provavelmente tem algum problema com essa pagina que seja melhor pular, talvez seja a capa.
        if pagina < indices[2]['Pagina']:
            continue

        texto_pagina = arquivo.pages[pagina].extract_text()
        texto_pagina = formata_pagina(texto_pagina)
        
        pdf_unido.extend(texto_pagina) #Adiciona o texto da pagina na lista de texto unido.

    pdf_unido = " ".join(pdf_unido) #Transforma a lista em uma string.

    return pdf_unido

def formata_pagina(texto_pagina,cabecalho=3,rodape=2):

    #Essa função serve para remover o cabeçalho e o rodapé da pagina.
    #Geralmente o cabeçalho é o nome da instituição, e o rodapé é o número da pagina, e ocupam esses espaços.
    #Mas, esse codigo pode ser melhorado, se tornando uma função que verifique qual é o cabeçalho e o rodapé, e remova eles.
    #Posso fazer isso vendo quais tem mais recorrencia nas paginas e a posição deles, se um padrão se repete muito no mesmo lugar, é o cabeçalho ou o rodapé.
    
    texto_pagina = texto_pagina.split("\n") 
    texto_pagina = texto_pagina[cabecalho:-rodape] #Remove o cabeçalho e o rodapé da pagina.
    
    return texto_pagina

def extrair_contexto(lista_materias, pagina): 

    #Essa função serve para extrair o contexto da materia, ou seja, a palavra anterior e posterior da materia.
    #Ela recebe a lista de materias, e a pagina, e retorna uma lista com o contexto de cada materia.
    #As materias estão separadas em uma string unica, antes dela possui o codigo, e posterior, o requisito.

    resultados = []
    for materia in lista_materias:  # Divide as matérias em uma lista
        # Expressão regular para encontrar a matéria com a palavra anterior e posterior
        materia = materia.strip() #Remove os espaços em branco
        padrao = rf"(\S+)\s+({re.escape(materia)})\s+(\S+)" #O Padrão que será buscado é esse: (Palavra anterior) (Materia) (Palavra posterior)
        correspondencia = re.search(padrao, pagina)

        if correspondencia:
            # Pega os grupos correspondentes (palavra anterior, matéria, palavra posterior)
            anterior, materia_encontrada, posterior = correspondencia.groups()
            resultados.append(f"{anterior} {materia_encontrada} {posterior}")
    
    return resultados

def checa_espacos(texto):

    #Essa função serve para verificar se o texto possui muitos espaços.
    #Ela retorna True se o texto possuir mais de 50% de espaços, isso significa que a pagina esta com erro.
    #Esta desse jeito: C A R A C T E R E S, pois o OCR pode ter feito isso.

    total_caracteres = len(texto)
    espacos = sum(1 for i in texto if i.isspace())
    if espacos > total_caracteres / 2:
        return True
    
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

def separador_materias(item):
    
    #Essa função serve para separar as materias, ele deve receber um capitulo do PPC e separar as Materias
    #Ela retorna uma lista de dicionários, onde cada dicionário contém o nome da matéria, a ementa, as horas, a bibliografia, o semestre, se é optativa e o conteúdo.
    #Formato: [{"Materia": "String", "Ementa": "String", "Horas": "String", "Bibliografia": "String", "Semestre": 1, "Optativa": False, "Conteudo": "String"}, ...]

    data_ppc = []
    contador_semestre = 0
    optativas = False
    
    if "SEMESTRE" in item:
        while "SEMESTRE" in item:
            semestres = separador_item(item,"SEMESTRE","SEMESTRE")
            item = item.replace(semestres,"")
            contador_semestre += 1
            while "Componente" in semestres:
                materias = separador_item(semestres,"Componente","Componente")
                
                semestres = semestres.replace(materias,"")
                if "Optativos" in materias:
                    optativas = True
                                
                materias = materias.replace("Componente  Curricular","").replace("Componente","").strip() #Remove o inicio da linha que é "Componente Curricular", e algumas "Componente" que ficaram.
                nome_materia = separador_item(materias,"Primeira","Horária").replace("Carga","")
                horas = separador_item(materias,"Horária","Ementa").replace("Horária","").strip()
                ementa = separador_item(materias,"Ementa","Bibliografia")
                bibliografia = separador_item(materias,"Bibliografia","Ultima")
                if "CORPO DOCENTE" in bibliografia:
                    bibliografia = separador_item(bibliografia,"Primeira","CORPO DOCENTE")

                if len(ementa) > 2:
                    data_ppc.append({
                    "materia": nome_materia,
                    "ementa": ementa,
                    "horas": horas,
                    "bibliografia": bibliografia,
                    "semestre": contador_semestre,
                    "optativa": optativas,
                    "conteudo": materias
                    })

    return data_ppc

def unir_elementos_materias(lista_materias,paginas_dados_materias):

    #Essa função serve para unir os elementos das materias, e os elementos dos requisitos.
    #Ela recebe a lista de materias, e as paginas com os dados das materias.
    #Recebe a lista de materias, e separa o nome de todas as materias.

    str_materias = [] #Lista que receberá os dados das materias.

    lista_nomes_materias = [materia["materia"] for materia in lista_materias]

    for pagina in paginas_dados_materias:
        str_materias.extend(extrair_contexto(lista_nomes_materias, pagina))

    str_materias = list(set(str_materias))

    return str_materias

def classificador_dados_materias(lista_string_materias):

    #Essa função serve para separar os dados das materias, e transformar eles em um dicionário.
    #Na parte anterior, os dados são separados em (Palavra anterior, Materia, Palavra posterior), e aqui, eu pego a palavra anterior e a posterior, e junto com a materia, eu crio um dicionário.
    #Esse dicionário contem o codigo da materia, o nome da materia, e o requisito da materia.

    lista_info_materias = []
    #Para cada item em str_materias, ele vai separar o codigo da materia, o nome da materia, e o requisito da materia.
    for item in lista_string_materias:
        item = item.strip()
        item = item.split(" ")

        #Caso a palavra anterior seja muito pequeno, ele não é um requisito, e sim as horas da materia.
        if len(item[-1]) < 3:

            codigo = item[0]
            
            item = item[:-1]
            item = item[1:]
            item = " ".join(item)
            
            dict_materia = {'codigo': codigo, 'nome': item, 'requisto': 'Nenhum'}

        #Caso a palavra anterior seja no tamanho maior que 3, ele é o requisito da materia.
        elif len(item[-1]) > 3:
            requisito = item[-1]
            codigo = item[0]
            
            item = item[:-1]
            item = item[1:]
            item = " ".join(item)

            dict_materia = {'codigo': codigo, 'nome': item, 'requisto': requisito}

        lista_info_materias.append(dict_materia)

    return lista_info_materias

def gerar_json_materias(lista_materias, lista_info_materias,nome_arquivo,curso):
    #Essa função serve para juntar as informações das materias, com as informações dos requisitos, e gerar o dicionario completo.
    #Ela recebe a lista de materias, a lista de informações das materias, e o numero do ID.
    #Ela retorna uma lista de dicionarios, onde cada dicionario contem todos os dados de materias unidos.

    dicionario_materias = []

    for item in lista_materias:
        materia_encontrada = False 

        for info in lista_info_materias:
            if item['materia'].strip() == info['nome'].strip():
                materia_completa = {
                    'nomeArquivo': nome_arquivo,
                    'tipoInformacao': 'Materia',
                    'curso': curso,
                    'codigo': info['codigo'],
                    'requisito': info['requisto']
                }
                materia_completa.update(item)
                dicionario_materias.append(materia_completa)
                materia_encontrada = True
                break

        if not materia_encontrada:
            materia_completa = {
                'nomeArquivo': nome_arquivo,
                'tipoInformacao': 'Materia',
                'curso': curso,
                'codigo': "",  # Código não encontrado
                'requisito': ""  # Requisito não encontrado
            }
            materia_completa.update(item)
            dicionario_materias.append(materia_completa)

    return dicionario_materias

def gerar_json_fatias(pdf_partes,tamanho_fatia=200): #Padrão de 200 caracteres.

    #Preciso atualizar essa função para que não armazene mais informações sobre o arquivo, somente as informações sobre a fatia.

    #Função que vai gerar o JSON das fatias do PDF.
    #Essa função recebe a lista de partes do PDF, e o numero do ID, que irá ser incrementado.
    #Ela retorna uma lista de dicionarios, onde cada dicionario contem as partes do PDF, e seus dados de origem.

    pdf_partes_fatiado = []

    for item in pdf_partes:
        conteudo_fatiado = fatiar_conteudo(item['conteudo'], tamanho_fatia)
        
        for parte in conteudo_fatiado:

            #Essa parte será modificada para salvar menos dados.

            novo_item = {
                'posicaoFatia': len(pdf_partes_fatiado) + 1,
                'pagina': item['pagina'],
                'conteudo': parte
            }

            pdf_partes_fatiado.append(novo_item)
    
    return pdf_partes_fatiado

if __name__ == "__main__":
    # Teste da função com um arquivo PDF específico
    ler_pdf('PPC-BSI_Camboriú.pdf')
