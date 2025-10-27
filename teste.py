from flask import Flask, render_template, request, jsonify
import json
import base64


app = Flask(__name__)

def simular_geracao_tts(texto):
    """
    Esta é uma função SIMULADA.
    Ela finge ser o Google Cloud TTS ou o Amazon Polly.
    Ela retorna um áudio falso (silêncio) e uma lista de visemas.
    
    No mundo real, você usaria a biblioteca do Google/Amazon aqui.
    """
    
    audio = "audios/EA008.wav"
    #abra o audio e leia como base64
    with open(audio, "rb") as audio_file:
        audio_content = audio_file.read()
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
    # No exemplo real, isso seria `audio_content = response.audio_content`
    # e `audio_base64 = base64.b64encode(audio_content).decode('utf-8')`

    # Vamos focar nos visemas, que são a parte importante.
    
    # 2. Visemas Falsos
    # Esta é a lista de "comandos" que o seu frontend vai usar.
    # O formato é: {"time": [em milissegundos], "value": [nome do visema]}
    # Vamos simular a frase "Olá mundo"
    visemas = [
        # Repetição 1 (0 - 5000ms)
        {"time": 0, "value": "sil"},
        {"time": 100, "value": "e"},
        {"time": 300, "value": "u"},
        {"time": 550, "value": "sil"},
        {"time": 700, "value": "t"},
        {"time": 850, "value": "e"},
        {"time": 1000, "value": "sil"},
        {"time": 1150, "value": "a"},
        {"time": 1350, "value": "m"},
        {"time": 1550, "value": "o"},
        {"time": 1750, "value": "sil"},
        {"time": 1900, "value": "v"},
        {"time": 2100, "value": "i"},
        {"time": 2300, "value": "t"},
        {"time": 2500, "value": "o"},
        {"time": 2700, "value": "j"},  # 'r' aproximado por 'j'
        {"time": 2900, "value": "i"},
        {"time": 3100, "value": "a"},
        {"time": 3400, "value": "sil"},
        {"time": 4800, "value": "sil"},

        # Repetição 2 (5000 - 10000ms)
        {"time": 5000, "value": "sil"},
        {"time": 5100, "value": "e"},
        {"time": 5300, "value": "u"},
        {"time": 5550, "value": "sil"},
        {"time": 5700, "value": "t"},
        {"time": 5850, "value": "e"},
        {"time": 6000, "value": "sil"},
        {"time": 6150, "value": "a"},
        {"time": 6350, "value": "m"},
        {"time": 6550, "value": "o"},
        {"time": 6750, "value": "sil"},
        {"time": 6900, "value": "v"},
        {"time": 7100, "value": "i"},
        {"time": 7300, "value": "t"},
        {"time": 7500, "value": "o"},
        {"time": 7700, "value": "j"},
        {"time": 7900, "value": "i"},
        {"time": 8100, "value": "a"},
        {"time": 8400, "value": "sil"},
        {"time": 9800, "value": "sil"},

        # Repetição 3 (10000 - 15000ms)
        {"time": 10000, "value": "sil"},
        {"time": 10100, "value": "e"},
        {"time": 10300, "value": "u"},
        {"time": 10550, "value": "sil"},
        {"time": 10700, "value": "t"},
        {"time": 10850, "value": "e"},
        {"time": 11000, "value": "sil"},
        {"time": 11150, "value": "a"},
        {"time": 11350, "value": "m"},
        {"time": 11550, "value": "o"},
        {"time": 11750, "value": "sil"},
        {"time": 11900, "value": "v"},
        {"time": 12100, "value": "i"},
        {"time": 12300, "value": "t"},
        {"time": 12500, "value": "o"},
        {"time": 12700, "value": "j"},
        {"time": 12900, "value": "i"},
        {"time": 13100, "value": "a"},
        {"time": 13400, "value": "sil"},
        {"time": 14800, "value": "sil"},

        # Repetição 4 (15000 - 20000ms)
        {"time": 15000, "value": "sil"},
        {"time": 15100, "value": "e"},
        {"time": 15300, "value": "u"},
        {"time": 15550, "value": "sil"},
        {"time": 15700, "value": "t"},
        {"time": 15850, "value": "e"},
        {"time": 16000, "value": "sil"},
        {"time": 16150, "value": "a"},
        {"time": 16350, "value": "m"},
        {"time": 16550, "value": "o"},
        {"time": 16750, "value": "sil"},
        {"time": 16900, "value": "v"},
        {"time": 17100, "value": "i"},
        {"time": 17300, "value": "t"},
        {"time": 17500, "value": "o"},
        {"time": 17700, "value": "j"},
        {"time": 17900, "value": "i"},
        {"time": 18100, "value": "a"},
        {"time": 18400, "value": "sil"},
        {"time": 19800, "value": "sil"},

        # Final exatamente em 20 segundos
        {"time": 20000, "value": "sil"}
    ]

    # O áudio precisa "durar" pelo menos 1400ms.
    # Vou usar um áudio de silêncio real (1 segundo) em base64.
    # Você pode encontrar "1 second silent mp3 base64" online.
    
    return {"audio_base64": audio_base64, "visemes": visemas}

# --- Rota Principal (para servir a página de teste) ---
@app.route('/')
def index():
    return render_template('visemas.html')

# --- Rota da API (para gerar a fala) ---
@app.route('/gerar-fala', methods=['POST'])
def api_gerar_fala():
    dados = request.get_json()
    texto = dados.get('texto')
    
    if not texto:
        return jsonify({"erro": "Nenhum texto fornecido"}), 400
        
    # --- Ponto de Substituição ---
    # Aqui é onde você chamaria a API real.
    # Em vez de `simular_geracao_tts`, você chamaria:
    # dados_tts = chamar_google_tts(texto)
    # ou
    # dados_tts = chamar_amazon_polly(texto)
    
    dados_tts = simular_geracao_tts(texto)
    
    return jsonify(dados_tts)

if __name__ == '__main__':
    app.run(debug=True)