import os, sys
import dotenv
from google.cloud import texttospeech

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #Serve para importar a pasta raiz.
from databases.bd_utils import get_colecao
dotenv.load_dotenv()

PROJECT_ID = os.getenv("ID_PROJETO")

def gera_audio_conversa(prompt, json_audio, output_filepath):

    dirpath = "audios" # Define o diretório padrão como 'audios' se nenhum diretório for especificado.
    os.makedirs(dirpath, exist_ok=True) 
    
    output_filepath = f"{dirpath}/{output_filepath}" # Atualiza o caminho do arquivo de saída para incluir o diretório.

    dialogo = json_audio['Detalhes']
    dialogo = dialogo['Audio']['Dialogo']
    
    next_speaker_idx = 1 # Índice para o primeiro locutor.
    speaker_map = {} # Mapeia os locutores originais para aliases.
    turnos_conversa = [] # Mapeia os turnos de conversa

    for turno in dialogo:
        # espera-se que cada turno tenha 'Personagem' e 'Fala'
        original_speaker = turno.get('Personagem') or turno.get('speaker') or 'Unknown'
        text = turno.get('Fala') or turno.get('text') or ''

        if original_speaker not in speaker_map:
            speaker_map[original_speaker] = f"Speaker{next_speaker_idx}"
            next_speaker_idx += 1
    
        alias = speaker_map[original_speaker]
        print(f"{alias} ({original_speaker}): {text}")
        turnos_conversa.append(
            texttospeech.MultiSpeakerMarkup.Turn(
                speaker=alias,
                text=text
            )
        )

    client = texttospeech.TextToSpeechClient() # Cria o cliente.

    synthesis_input = texttospeech.SynthesisInput( # Define a entrada de síntese.
        multi_speaker_markup=texttospeech.MultiSpeakerMarkup(turns=turnos_conversa),
        prompt=prompt,
    )

    # Configuração de voz para múltiplos locutores.
    multi_speaker_voice_config = texttospeech.MultiSpeakerVoiceConfig( 
        speaker_voice_configs=[
            texttospeech.MultispeakerPrebuiltVoice( #Vozes predefinidas do Gemini.
                speaker_alias="Speaker1",
                speaker_id="Algenib",
            ),
            texttospeech.MultispeakerPrebuiltVoice( 
                speaker_alias="Speaker2",
                speaker_id="Autonoe",
            ),
        ]
    )

    audio_config = texttospeech.AudioConfig( # Se quiser modificar para .mp3, basta alterar aqui.
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=24000,
    )

    # Configuração da voz e do áudio.
    voice = texttospeech.VoiceSelectionParams(
        language_code="pt-BR", # Aqui modifica o idioma da voz.
        model_name="gemini-2.5-flash-tts", 
        multi_speaker_voice_config=multi_speaker_voice_config,
    )

    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Salva o conteúdo de áudio em um arquivo.
    with open(output_filepath, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio salvo em: {output_filepath}")

    return output_filepath


# Teste consumindo os dados do MongoDB e filtrando apenas atividades de áudio.
# if __name__ == "__main__":
#     atividades = get_colecao('atividades_detalhadas') # Só pra não dar
    # for atividade in atividades:
    #     print (f"Tipo de Atividade: {atividade['Atividade']}")
    #     if (atividade["Atividade"]) == "Audio": #Verifica se é atividade de áudio.
                
    #             print (atividade)
    #             print ("Gerando áudio para a atividade...")
    #             output_path = f"{atividade.get('Codigo','unknown')}.wav"
    #             try:
    #                     gera_audio_conversa(
    #                             prompt="Uma conversa tranquila e divertida entre professor e aluno.",
    #                             json_audio=atividade,
    #                             output_filepath=output_path
    #                     )
    #                     # adiciona o caminho do áudio ao objeto antes de salvar no banco
    #                     atividade["AudioPath"] = os.path.abspath(output_path)
    #                     atividade["AudioStatus"] = "generated"
    #             except Exception as e:
    #                     # registra erro no objeto para depuração, mas continua o pipeline
    #                     atividade["AudioStatus"] = "error"
    #                     atividade["AudioError"] = str(e)

    #                     print (f"Erro ao gerar áudio: {e}")