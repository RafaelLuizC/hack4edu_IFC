import os
from util.helpers import *
from util.prompts import *
from pdf_parser.pdf import extrair_dados_pdf
from databases.bd_utils import *
from AI.gemini import generate
from AI.gemini_audio import gera_audio_conversa

# Aqui se insere o perfil do usuário, ele pode definir preferências de aprendizado, interesses e objetivos.
# perfil_do_usuario ="""Rafael Luiz, tem 26 anos e quer aprender mais sobre Estatistica e Probabilidade para se sair bem em suas aulas no IFC,
# gosta de bicicletas, jogos de tabuleiro e tecnologia.
# Prefere aprender por meio de exemplos práticos."""

perfil_do_usuario ="""Vitória Pereira, tem 23 anos e quer aprender mais sobre Estatística e Probabilidade para se sair bem em suas aulas no IFC,
gosta de novelas, música e tecnologia.
"""

def pipeline_tarefas(texto_referencia, perfil_usuario):

    # Primeira etapa do Pipeline: Extrair texto do PDF e corrigir ele.
    print ("Lendo texto do PDF...")
    texto_extraido = extrair_dados_pdf(texto_referencia) 
    texto_extraido = ' '.join(texto_extraido) # Concatena a lista em uma string única.

    # --- Gerar Tópicos de Estudo ---
    # Nessa etapa, o sistema gera os tópicos de estudo a partir do texto extraído do PDF.
    # Ele tambem analisa os exemplos do professor para entender o estilo de ensino.
    
    # Primeira interação com modelos de Linguagem Generativa.
    topicos_gerados = generate(texto_extraido, prompt_parser()) 

    topicos_gerados = trata_json_resposta(topicos_gerados)

    # Salva os tópicos gerados no banco de dados.
    for item in topicos_gerados:
        # A função se chama inserir_logs, pq peguei de outro codigo.
        inserir_dados('atividades_parser', item)

    # Aqui eu estou considerando somente o primeiro tópico gerado, mas o ideal seria criar um algoritmo para selecionar o melhor tópico.
    item = topicos_gerados[0] 
    print (f"O item 0 é: {item}")

    # --- Gerar Trilha de Aprendizado ---
    # Nessa etapa, o sistema gera a trilha de aprendizado baseada nos tópicos gerados anteriormente.
    # Ele define quais atividades serão criadas para o topico, o topico abordado e o perfil do usuario.
    print ("\nGerando trilha de aprendizado...\n")

    # Aqui ele recebe o um dos topicos gerados.
    # O perfil do usuário é inserido no prompt para personalizar a trilha de aprendizado.
    # E o tema é o tópico específico que está sendo abordado.
    trilha_aprendizado = generate(topicos_gerados, prompt_trilha().replace("[SUBSTITUIR-PERFIL-USUARIO]", perfil_usuario).replace("[SUBSTITUIR-TEMA]", item["Topico"]))
    trilha_aprendizado = trata_json_resposta(trilha_aprendizado) # Converte a resposta em JSON.

    #Salva a trilha de aprendizado no banco de dados.
    for item in trilha_aprendizado: #Para cada item na trilha de aprendizado.
        inserir_dados('trilhas_aprendizado', item)

    # --- Gerar Atividades Detalhadas ---
    print ("\nGerando atividades detalhadas...\n")

    # Aqui é a terceira interação com o modelo de linguagem generativa.
    # Ele gera as atividades detalhadas baseadas na trilha de aprendizado criada anteriormente.
    # Cada atividade inclui instruções, recursos e, se aplicável, dados para geração de áudio.
    atividades = generate(str(trilha_aprendizado), prompt_atividades())
    atividades = trata_json_resposta(atividades) # Converte a resposta em JSON.

    # Salva as atividades detalhadas no banco de dados.
    for atividade in atividades:
        if (atividade["Atividade"]) == "Audio": # Se a atividade for de áudio, deve passar por um processo extra.
                print ("Gerando áudio para a atividade...")
                output_path = f"{atividade.get('Codigo','unknown')}.wav" # Define o nome do arquivo de áudio.
                try: # Gera o áudio usando a função do gemini_audio.py
                        gera_audio_conversa(
                                prompt="Uma conversa tranquila e divertida entre professor e aluno.",
                                json_audio=atividade,
                                output_filepath=output_path
                        )
                        # Adiciona o caminho do áudio ao objeto antes de salvar no banco.
                        atividade["AudioPath"] = os.path.abspath(output_path)
                        atividade["AudioStatus"] = "generated"                
                
                # Registra erro no objeto para depuração, mas continua a inserção no banco.
                except Exception as e:
                        # Modificar no Frontend depois, mas em caso de erro, é possivel usar a transcrição do navegador.
                        atividade["AudioStatus"] = "error"
                        atividade["AudioError"] = str(e) # Adiciona a mensagem de erro.
        
        # Nenhuma das outras atividades precisam de processamento extra, então insere direto no banco.
        inserir_dados('atividades_detalhadas', atividade)

if __name__ == "__main__":

  # PDF Path é o caminho do PDF que será processado.
  pdf_path = "pdf_sample/Lista3Estatistica.pdf"
  
  # Ele ta salvando no MongoDB, para salvar, é necessario verificar a pasta databases/bd_utils.py.
  # Nele tem a função inserir_logs, que salva os dados no MongoDB, se quiser modificar os dados de conexão, é só alterar lá.

  # Não retorna nada, apenas executa a pipeline de tarefas.
  pipeline_tarefas(pdf_path, perfil_do_usuario)