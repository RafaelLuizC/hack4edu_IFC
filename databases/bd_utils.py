from pymongo import MongoClient
from datetime import datetime, timedelta
import json

def inserir_logs(collection_name, dados):
    
    # Função para inserir logs no Banco de Dados MongoDB.
    # Ela conecta no banco de dados 'H4E_DB' e insere os dados na coleção especificada, antes servia para Logs, mas foi adaptada para inserir qualquer dado.

    client = MongoClient('localhost', 27017)
    db = client['H4E_DB_v2'] #Nome do Banco de Dados

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
    db = client['H4E_DB_v2'] #Nome do Banco de Dados
    colecao = db[colecao]

    resultado = colecao.delete_many({})

    print(f"{resultado.deleted_count} documentos foram deletados.")

    client.close()



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
    db = client['H4E_DB_v2'] #Nome do Banco de Dados
    colecao = db[colecao]

    for doc in colecao.find():
        dados.append(doc)

    dados = json.loads(json.dumps(dados, default=str)) #Converte os dados para JSON serializável.

    client.close()

    return dados


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

    colecao = input("Digite a coleção que deseja resetar no banco de dados 'H4E_DB_v2': ")
    resetar_bd(colecao)

    print ("Banco de dados resetado.")
