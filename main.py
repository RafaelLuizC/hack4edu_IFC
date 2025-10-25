import json, os, dotenv, time, sys, re
from util.helpers import *
from util.prompts import *
from pdf_parser.pdf import extrair_dados_pdf
from databases.bd_utils import *
from AI.gemini import generate
from AI.gemini_audio import gera_audio_conversa

perfil_do_usuario ="""Rafael Luiz, tem 26 anos e quer aprender mais sobre Estatistica e Probabilidade para se sair bem em suas aulas no IFC,
gosta de bicicletas, jogos de tabuleiro e tecnologia.
Prefere aprender por meio de exemplos práticos."""

def pipeline_tarefas(texto_referencia, perfil_usuario):

    print ("Lendo texto do PDF...")
    texto_extraido = extrair_dados_pdf(texto_referencia)
    texto_extraido = ' '.join(texto_extraido)

    texto_corrigido = generate(texto_extraido, prompt_parser())

    texto_corrigido = trata_json_resposta(texto_corrigido)

    #Salva o texto corrigido no banco de dados.
    for item in texto_corrigido:
        #A função se chama inserir_logs, pq peguei de outro codigo.
        inserir_logs('atividades_parser', item)

    item = texto_corrigido[0] #Pega o primeiro item da lista, mas isso é porque não fiz um algoritmo para isso ainda.

    print (f"O item 0 é: {item}")

    # --- Gerar Trilha de Aprendizado ---

    print ("\nGerando trilha de aprendizado...\n")

    trilha_aprendizado = generate(texto_corrigido, prompt_trilha().replace("[SUBSTITUIR-PERFIL-USUARIO]", perfil_usuario).replace("[SUBSTITUIR-TEMA]", item["Topico"]))
    trilha_aprendizado = trata_json_resposta(trilha_aprendizado)

    #Salva a trilha de aprendizado no banco de dados.
    for item in trilha_aprendizado: #Para cada item na trilha de aprendizado.
        inserir_logs('trilhas_aprendizado', item)

    # --- Gerar Atividades Detalhadas ---

    print ("\nGerando atividades detalhadas...\n")

    atividades = generate(str(trilha_aprendizado), prompt_atividades())

    atividades = trata_json_resposta(atividades)

    #Salva as atividades detalhadas no banco de dados.
    for atividade in atividades:
        
        print (f"Tipo de Atividade: {atividade['Atividade']}")
        if (atividade["Atividade"]) == "Audio": #Verifica se é atividade de áudio.
                
                print (atividade)

                print ("Gerando áudio para a atividade...")
                os.makedirs("audios", exist_ok=True)
                output_path = f"audios/{atividade.get('Codigo','unknown')}.wav"
                try:
                        gera_audio_conversa(
                                prompt="Uma conversa em portugues entre dois personagens a respeito de Conceitos Básicos de Probabilidade",
                                json_audio=atividade,
                                output_filepath=output_path
                        )
                        # adiciona o caminho do áudio ao objeto antes de salvar no banco
                        atividade["AudioPath"] = os.path.abspath(output_path)
                        atividade["AudioStatus"] = "generated"
                except Exception as e:
                        # registra erro no objeto para depuração, mas continua o pipeline
                        atividade["AudioStatus"] = "error"
                        atividade["AudioError"] = str(e)

        inserir_logs('atividades_detalhadas', atividade)


if __name__ == "__main__":

  # PDF Path é o caminho do PDF que será processado.
  pdf_path = "pdf_sample/Atividade3Matematica.pdf"
  
  # Ele ta salvando no MongoDB, para salvar, é necessario verificar a pasta databases/bd_utils.py.
  # Nele tem a função inserir_logs, que salva os dados no MongoDB, se quiser modificar os dados de conexão, é só alterar lá.

  #Não retorna nada, apenas executa a pipeline de tarefas.
  pipeline_tarefas(pdf_path, perfil_do_usuario)