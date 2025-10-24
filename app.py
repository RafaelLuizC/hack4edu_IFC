from flask import Flask, render_template, send_from_directory, jsonify
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
    with open('data/trilha.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)