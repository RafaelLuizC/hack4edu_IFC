from flask import Flask, render_template, send_from_directory, jsonify
from databases.bd_utils import todos_os_dados
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activity/<codigo>')
def activity(codigo):
    return render_template('activity.html', codigo=codigo)

@app.route('/trilha.json')
def trilha_json():
    data = todos_os_dados('atividades_detalhadas')
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)