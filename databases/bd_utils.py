from pymongo import MongoClient
from datetime import datetime, timedelta
import json

def inserir_logs(collection_name, dados):
    
    # Função para inserir logs no Banco de Dados MongoDB.
    # Ela conecta no banco de dados 'H4E_DB' e insere os dados na coleção especificada, antes servia para Logs, mas foi adaptada para inserir qualquer dado.

    client = MongoClient('localhost', 27017)
    db = client['H4E_DB'] #Nome do Banco de Dados

    try:
        print (f"Inserindo log na coleção '{collection_name}'")
        db[collection_name].insert_one(dados)
    except Exception as e:
        print(f"Erro ao inserir log: {e}")
        print(f"Dados: {dados}") 
    
    finally:
        client.close() #Para evitar vazamento.

    return

def resetar_bd(colecao):

    # Serve para deletar todos os dados, função criada SOMENTE PARA OS TESTES.
    # Por padrão deleta no banco de dados 'meu_banco' e 'minha_colecao'.

    # CUIDADO COM ESSA FUNÇÃO, POIS ELA DELETA TODOS OS DADOS DA COLEÇÃO.

    client = MongoClient('localhost', 27017)
    db = client['meu_banco']
    colecao = db[colecao]

    resultado = colecao.delete_many({})

    print(f"{resultado.deleted_count} documentos foram deletados.")

    client.close()

def filtrar_ids_mongodb(area: str = None, data: str = None):
    client = MongoClient('localhost', 27017)
    db = client['meu_banco']
    query = {}

    # Filtro por área
    if area is None:
        # Busca todos os IDs do banco de dados
        documentos = db.pages.find({}, {"_id": 0, "faiss_global_id": 1})
        ids_faiss = [doc["faiss_global_id"] for doc in documentos]
        print(f"Busca sem filtro de área - retornando todos os IDs")
        return ids_faiss
    else:
        area = area.lower()
        if "," in area:
            areas = [a.strip() for a in area.split(",")]
            query["area"] = {"$in": areas}
        else:
            query["area"] = area

        # Verificar se a área resulta em apenas um documento
        count = db.pages.count_documents(query)
        if count == 1:
            documentos = db.pages.find(query, {"_id": 0, "faiss_global_id": 1})
            ids_faiss = [doc["faiss_global_id"] for doc in documentos]
            print(f"Área única encontrada - ignorando filtro de data")
            return ids_faiss

    # Filtro por data (só aplica se não tiver encontrado área única)
    if data:
        # Caso 1: Filtro por ano específico
        if data.isdigit() and len(data) == 4:
            query["$or"] = [
                {"data": {"$regex": f".*{data}$"}},
                {"data": "Não foi encontrada a data"}  # Inclui documentos sem data
            ]
        
        # Caso 2: Filtro por conteúdo recente
        elif data.lower() in ["recentes", "no momento", "agora"]:
            data_limite = datetime.now() - timedelta(days=180)
            query["$expr"] = {
                "$or": [
                    {"$gte": [
                        {"$dateFromString": {
                            "dateString": "$data",
                            "format": "%d/%m/%Y"
                        }},
                        data_limite
                    ]},
                    {"$eq": ["$data", "Não foi encontrada a data"]}  # Inclui documentos sem data
                ]
            }
        
        # Caso 3: Filtro por período (últimos X meses)
        elif "últimos" in data.lower():
            try:
                meses = int(data.split()[1])
                periodo = datetime.now() - timedelta(days=30*meses)
                query["$expr"] = {
                    "$or": [
                        {"$gte": [
                            {"$dateFromString": {
                                "dateString": "$data",
                                "format": "%d/%m/%Y"
                            }},
                            periodo
                        ]},
                        {"$eq": ["$data", "Não foi encontrada a data"]}  # Inclui documentos sem data
                    ]
                }
            except:
                pass
    else:
        # Filtro padrão: últimos 12 meses + documentos sem data
        query["$or"] = [
            {"data": {"$regex": ".*2025$"}},  # Ano atual
            {"data": "Não foi encontrada a data"}
        ]

    # Executa a consulta
    documentos = db.pages.find(query, {"_id": 0, "faiss_global_id": 1})
    ids_faiss = [doc["faiss_global_id"] for doc in documentos]
    
    print(f"Encontrados {len(ids_faiss)} IDs para área='{area}' e data='{data}'")

    if not ids_faiss:
        documentos = db.pages.find({}, {"_id": 0, "faiss_global_id": 1})
        ids_faiss = [doc["faiss_global_id"] for doc in documentos]
        print(f"Nenhum ID encontrado com os filtros aplicados - retornando todos os IDs")
    
    return ids_faiss

def inserir_dados(data, string_colecao): #data é uma lista de dicionários, string_colecao é o nome da coleção.

    #Função para inserir os dados no Banco de Dados.
    #Recebe o item data, que deve conter uma lista de dicionários.
    # Por padrão insere no banco de dados 'meu_banco'  

    client = MongoClient('localhost', 27017)
    db = client['meu_banco']
    colecao = db[string_colecao]

    id_sequencial = ultimo_id_sequencial(string_colecao)
    
    if id_sequencial is None:
        print ("Nenhum documento encontrado.")
        id_sequencial = 1
    
    for item in data:
        item['idSequencial'] = id_sequencial
        colecao.insert_one(item)
        id_sequencial += 1

    client.close()

def busca_id_faiss(pesquisa):
    
    #Função para buscar os dados no Banco de Dados.
    #Recebe o item pesquisa, que deve conter um dicionário.
    #Por padrão busca no banco de dados 'meu_banco' e na coleção 'minha_colecao'.

    pesquisa = {"faiss_global_id": pesquisa}

    client = MongoClient('localhost', 27017)
    db = client['meu_banco']
    colecao = db['pages']

    item = colecao.find_one(pesquisa)   #Preciso modificar a pesquisa para não ser necessario adicionar o texto no argumento.

    if item:
        pass
    else:
        print("Nenhum documento encontrado.")

    client.close()

    return item

def busca_id(pesquisa):
    
    #Função para buscar os dados no Banco de Dados.
    #Recebe o item pesquisa, que deve conter um dicionário.
    #Por padrão busca no banco de dados 'meu_banco' e na coleção 'minha_colecao'.

    client = MongoClient('localhost', 27017)
    db = client['meu_banco']
    colecao = db['pages']

    item = colecao.find_one(pesquisa)   #Preciso modificar a pesquisa para não ser necessario adicionar o texto no argumento.

    if item:
        pass
    else:
        print("Nenhum documento encontrado.")

    client.close()

    return item

def todos_os_dados(colecao):
    
    #Função para buscar todos os dados no Banco de Dados.
    #Por padrão busca no banco de dados 'meu_banco' e na coleção 'minha_colecao'.

    dados = []

    client = MongoClient('localhost', 27017)
    db = client['meu_banco']
    colecao = db[colecao]

    for doc in colecao.find():
        dados.append({"ID": doc["idSequencial"], "Conteudo": doc["conteudo"]})

    client.close()

    return dados


def buscar_strings_semelhantes(pesquisa):

    #Função para buscar os dados no Banco de Dados.
    #Recebe o item pesquisa, que deve conter um dicionário.
    #Por padrão busca no banco de dados 'meu_banco' e na coleção 'minha_colecao'.
    client = MongoClient('localhost', 27017)

    pesquisa = (f'.*{pesquisa}.*')

    db = client['meu_banco']
    colecao = db['minha_colecao']

    for doc in colecao.find({"Nome": {"$regex": pesquisa}}):
        print(doc["Nome"])

    client.close()

def ultimo_id_sequencial(colecao):
    # Função para buscar o último id_sequencial no Banco de Dados.
    # Por padrão busca no banco de dados 'meu_banco' e na coleção 'minha_colecao'.

    client = MongoClient('localhost', 27017)
    db = client['meu_banco']
    colecao = db[colecao]

    ultimo_documento = colecao.find_one(sort=[("idSequencial", -1)])

    client.close()

    if ultimo_documento:
        return ultimo_documento["idSequencial"]
    else:
        return None


if __name__ == '__main__':

    colecao = input("Digite o nome da coleção: ")

    resetar_bd(colecao)
    
    # # with open ('json/pdf_slices.json', encoding='utf-8') as f:
    # with open ('data2.json', encoding='utf-8') as arquivo:
    #     data = json.load(arquivo)

    # inserir_dados(data, 'editais')

    # client = MongoClient('localhost', 27017)
    # db = client['meu_banco']
    # colecao = db['minha_colecao']

    # # pesquisa = "Materias"
    # # # pesquisa = (f'.*{pesquisa}.*')

    # # for doc in colecao.find({"Curso": "BSI"}):
    # #     print(doc)