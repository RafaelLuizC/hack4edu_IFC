from sentence_transformers import SentenceTransformer
import numpy as np
import json

def busca_vetor(string_pesquisa):

  print("Iniciou o processo de Vetorização.")

  model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

  with open('data_ppc.json', 'r', encoding='utf-8') as file:  # Ele pega o arquivo Data.Json e transforma em um item.
    data = json.load(file)

  similarities = []
  string_pesquisa = model.encode(string_pesquisa)
  max_similarity = 0
  for item_bd in data:
    item = item_bd["Conteudo"]
    embeddings = model.encode(item)

    # Calcular a similaridade entre os embeddings
    similarity = np.dot(embeddings, string_pesquisa) / (np.linalg.norm(embeddings) * np.linalg.norm(string_pesquisa))
    #print(f"Similaridade: {similarity}")
    #print(f"Item: {item}")
    similarities.append((similarity, item_bd))
    
    if similarity > max_similarity:
      max_similarity = similarity
      best_match = item_bd["Conteudo"]

  return best_match