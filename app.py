"""Simple Flask chat app (MySQL-backed).

This module serves a minimal chat HTTP API that persists messages to a
MySQL database. It is intended to be run directly (development) or inside
a container via Docker Compose where MySQL credentials are provided as
environment variables.

Operational notes:
- Expects MySQL reachable at `MYSQL_HOST` with credentials from env.
- Creates database `chat_db` and table `messages` if missing.
- Provides two routes for chat messages: POST to add and GET to read.
"""

from flask import Flask, request, render_template
from datetime import datetime

import mysql.connector
import os

app = Flask(__name__)

# MySQL config read from environment variables so Docker Compose can set them.
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'root'),
    'database': os.environ.get('MYSQL_DATABASE', 'chat_db')
}


def init_db():
    """Ensure the `chat_db` database and `messages` table exist.

    This function connects using the host/user/password to create the
    database (if missing) and then creates the table used to store chat
    messages. It is intentionally idempotent.
    """
    conn = mysql.connector.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password']
    )
    cursor = conn.cursor()
    # Create the database if it's not present
    cursor.execute("CREATE DATABASE IF NOT EXISTS chat_db")
    # Switch to the database and create the messages table
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
    """Serve the static client page."""
    return render_template('index.html')


@app.route('/<room>', methods=['GET'])
def room_html(room):
    """Serve the same static client for any room URL (client handles room selection)."""
    return render_template('index.html')


@app.route('/api/chat/<room>', methods=['POST'])
def post_chat(room):
    """Receive a form-encoded chat message and persist it to MySQL.

    Expected form fields: `username`, `msg`.
    Returns 400 on missing fields, 204 on success.
    """
    username = request.form.get('username')
    message = request.form.get('msg')
    if not username or not message:
        return 'Missing username or message', 400
    now = datetime.now()
    # Insert into MySQL using parameterized query to avoid injection
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
    """Return the chat history for `room` as plain text lines.

    Each line is formatted as: [YYYY-mm-dd HH:MM:SS] username: message
    """
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
    # Run the Flask dev server. In production use a WSGI server instead.
    app.run(host='0.0.0.0', port=5000, debug=True)
