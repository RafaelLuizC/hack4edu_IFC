import os, json, re
import dotenv
from google.cloud import texttospeech

dotenv.load_dotenv()

PROJECT_ID = os.getenv("ID_PROJETO")

def gera_audio_conversa(prompt, dialogo, output_filepath= "output_turn_based.wav"):

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

        turns.append(
            texttospeech.MultiSpeakerMarkup.Turn(
                speaker=alias,
                text=text
            )
        )

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(
        multi_speaker_markup=texttospeech.MultiSpeakerMarkup(turns=turns),
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
        ]
    )

    # Configuração da voz e do áudio.
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        model_name="gemini-2.5-flash-tts",
        multi_speaker_voice_config=multi_speaker_voice_config,
    )

    response = client.synthesize_speech(input=synthesis_input, voice=voice)

    # Salva o conteúdo de áudio em um arquivo.
    with open(output_filepath, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to file: {output_filepath}")

def json_to_dict(string_json):
    #Abre o arquivo json e converte em dicionario python, não é necessario limpar ele, só converter.
    with open(string_json, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            # Levanta um erro mais claro para o usuário sobre conteúdo inválido
            raise ValueError(f"Falha ao decodificar JSON de '{string_json}': {e}") from e
    return data


audio_data = json_to_dict('audio.json')

dialogo = audio_data['Detalhes']
dialogo = dialogo['Audio']['Dialogo']

turns = []

speaker_map = {}
next_speaker_idx = 1


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

    turns.append(
        texttospeech.MultiSpeakerMarkup.Turn(
            speaker=alias,
            text=text
        )
    )

gera_audio_conversa(
    prompt="Uma conversa em portugues entre dois personagens a respeito de Conceitos Básicos de Probabilidade",
    turns=turns,
    output_filepath="dialogue_output.wav"
)