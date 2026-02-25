# Implemented by GitHub Copilot
from flask import Flask, request, send_file, jsonify
from datetime import datetime
import os

app = Flask(__name__)

CHAT_DIR = 'chat_data'
if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

@app.route('/', methods=['GET'])
def index():
    return send_file('index.html')

@app.route('/<room>', methods=['GET'])
def room_html(room):
    return send_file('index.html')

@app.route('/api/chat/<room>', methods=['POST'])
def post_chat(room):
    username = request.form.get('username')
    message = request.form.get('msg')
    if not username or not message:
        return 'Missing username or message', 400
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{now}] {username}: {message}'
    room_file = os.path.join(CHAT_DIR, f'{room}.txt')
    with open(room_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    return '', 204

@app.route('/api/chat/<room>', methods=['GET'])
def get_chat(room):
    room_file = os.path.join(CHAT_DIR, f'{room}.txt')
    if not os.path.exists(room_file):
        return '', 200
    with open(room_file, 'r', encoding='utf-8') as f:
        chat = f.read()
    return chat, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
