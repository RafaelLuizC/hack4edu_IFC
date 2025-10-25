import os, sys
import dotenv
from google.cloud import texttospeech

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #Serve para importar a pasta raiz.
dotenv.load_dotenv()

PROJECT_ID = os.getenv("ID_PROJETO")

def gera_audio_conversa(prompt, json_audio, output_filepath):

    dirpath = os.path.dirname(output_filepath)
    if not dirpath:
        dirpath = "audios"

    os.makedirs(dirpath, exist_ok=True)

    dialogo = json_audio['Detalhes']
    dialogo = dialogo['Audio']['Dialogo']
    
    next_speaker_idx = 1 # Índice para o primeiro locutor.
    speaker_map = {} # Mapeia os locutores originais para aliases.
    turnos_conversa = [] # Mapeia os turnos de conversa

    for turno in dialogo:
        original_speaker = turno['Personagem']
        text = turno['Fala']

        if original_speaker not in speaker_map:
            if next_speaker_idx == 1:
                speaker_map[original_speaker] = "Speaker1"
            elif next_speaker_idx == 2:
                speaker_map[original_speaker] = "Speaker2"
            else:
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

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(
        multi_speaker_markup=texttospeech.MultiSpeakerMarkup(turns=turnos_conversa),
        prompt=prompt,
    )

    # Configuração de voz para múltiplos locutores.
    multi_speaker_voice_config = texttospeech.MultiSpeakerVoiceConfig(
        speaker_voice_configs=[
            texttospeech.MultispeakerPrebuiltVoice(
                speaker_alias="Speaker1",
                speaker_id="Algenib",
            ),
            texttospeech.MultispeakerPrebuiltVoice(
                speaker_alias="Speaker2",
                speaker_id="Autonoe",
            ),
            texttospeech.MultispeakerPrebuiltVoice(
                speaker_alias="Speaker3",
                speaker_id="Bellatrix",
            )
        ]
    )

    print ("Gerando áudio com múltiplos locutores...")

    # Configuração da voz e do áudio.
    voice = texttospeech.VoiceSelectionParams(
        language_code="pt-BR",
        model_name="gemini-2.5-flash-tts",
        multi_speaker_voice_config=multi_speaker_voice_config,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=24000,
    )

    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Salva o conteúdo de áudio em um arquivo.
    with open(output_filepath, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio salvo em: {output_filepath}")

    return output_filepath