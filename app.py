from flask import Flask, render_template, send_from_directory, jsonify
# from databases.bd_utils import get_colecao # Para rodar com o banco de dados, descomente esta linha.
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activity/<codigo>')
def activity(codigo):
    return render_template('activity.html', codigo=codigo)

@app.route('/atividades')
def trilha_json():
    # Aqui você pode buscar os dados do banco de dados.
    # data = get_colecao('atividades_detalhadas') # Descomente esta linha para rodar com o banco de dados.

    # Esta rota retorna a trilha de atividades em formato JSON, para testes.
    with open ('data/sample_atividades.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)