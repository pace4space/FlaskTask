# Implemented by GitHub Copilot

from flask import Flask, request, send_file
from datetime import datetime

import mysql.connector
import os

app = Flask(__name__)

# MySQL config from environment (for Docker Compose)
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'root'),
    'database': os.environ.get('MYSQL_DATABASE', 'chat_db')
}

# Ensure DB and table exist
def init_db():
    conn = mysql.connector.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password']
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS chat_db")
    conn.database = MYSQL_CONFIG['database']
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        room VARCHAR(64),
        username VARCHAR(20),
        message VARCHAR(120),
        timestamp DATETIME
    )''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()


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
    now = datetime.now()
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (room, username, message, timestamp) VALUES (%s, %s, %s, %s)",
        (room, username, message, now)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return '', 204


@app.route('/api/chat/<room>', methods=['GET'])
def get_chat(room):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, username, message FROM messages WHERE room=%s ORDER BY id ASC",
        (room,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    lines = []
    for ts, username, msg in rows:
        ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f'[{ts_str}] {username}: {msg}')
    return '\n'.join(lines), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
