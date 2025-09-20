from transformers import pipeline
import torch
import os
import json

from util.prompts import *
from util.helpers import *

#Usar um prompt para cada interação do usuario ele procurar por informações do usuario.
#O Prompt deve receber o contexto da conversa, e a resposta do usuario e procurar por dados nele.
#Inserir no prompt dados que o usuario pode ter esquecido de mencionar, como o nome dele, que sejam necessarios para a ação que ele deseja realizar.
#Criar uma especie de sistema que necessite de id para acessar certas partes, e com o retorno do dado faltante o prompt irá perguntar ao usuario e checar se ele respondeu.
#Criar um sistema de verificação de dados, para que o usuario possa confirmar se os dados que ele inseriu estão corretos.

#O prompt terá uma lista de dados que é necessario, a estrutura do dado por exemplo 2022010820 Matricula do aluno, e o prompt irá perguntar ao usuario se ele deseja inserir esse dado.


def resposta_local(mensagem):
  lista_itens_recuperados = [] #Lista de itens recuperados pela busca de vetores.

  texto = chat_ia(analise_perguntas(mensagem)) #Chama a função de análise de perguntas e passa a mensagem do usuário como parâmetro.

  print (f'Esse é o texto: {texto}')

  texto = texto.replace("Output:","") #Remove a palavra Output do texto.

  print (f"Esse é o texto Depois: {texto}")

  try:
    json_texto = json.loads(texto)
    print (f"Esse é o texto JSON: {json_texto}")
 
  except json.JSONDecodeError:
    print (f"A tentativa de converter o texto em JSON falhou.\n {texto}")

#Preciso modificar essa função para que ela receba o Contexto, e a pergunta.
def chat_ia(contexto):

  pipe = pipeline("text-generation", model="microsoft/Phi-3.5-mini-instruct", trust_remote_code=True)

  outputs = pipe(
      contexto,
      max_new_tokens=500,
      do_sample=False  , #Gera mais de uma resposta caso esteja "True"
      #temperature=0.8, #0.0 é o padrão, quanto maior, mais aleatório
      #top_k= 40,
      #top_p=0.90,
  )
  print (outputs[0]["generated_text"])
  return outputs[0]["generated_text"][-1]["content"]

if "__main__" == __name__:

  texto = input("Digite a pergunta: ")

  categorias = "Inscrição" #Esse dado serviria para a IA saber qual categoria ela deve buscar, mas como o codigo não esta pronto ainda não é necessario.

  texto = chat_ia(analise_perguntas(categorias,texto))
  
  #print (texto)
  #
  #texto_json = json.loads(texto)
  #for item in texto_json:
  #  print (f"{item}")

  item_recuperado = busca_vetor(texto)

  # Limpa a tela
  #os.system('cls')
  #print (item_recuperado)
  resposta = (chat_ia(prompt_geracao_conteudo(item_recuperado,texto)))
  print (f"Pergunta: {texto}")
  print (f"Resposta: {resposta}")


  # Salva os dados em um arquivo Excel, Relatorio com as perguntas e respostas geradas.
  relatorio_perguntas_respostas(texto, resposta)