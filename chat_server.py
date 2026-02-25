"""File-backed chat server.

This lightweight Flask app stores chat messages as text files under
the `chat_data/` directory. Each chat room is a separate file named
`<room>.txt` and contains one message per line.

Useful for local testing or demos when a database is not required.
"""

from flask import Flask, request, render_template, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Directory where per-room chat files are stored. Created if missing.
CHAT_DIR = 'chat_data'
if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)


@app.route('/', methods=['GET'])
def index():
    """Serve the web client from the `templates` folder."""
    return render_template('index.html')


@app.route('/<room>', methods=['GET'])
def room_html(room):
    """Serve the same client for any room path (client picks the room)."""
    return render_template('index.html')


@app.route('/api/chat/<room>', methods=['POST'])
def post_chat(room):
    """Append a message to the room file.

    Expects form-encoded `username` and `msg`. Writes a single line with
    a timestamp and returns HTTP 204 on success.
    """
    username = request.form.get('username')
    message = request.form.get('msg')
    if not username or not message:
        return 'Missing username or message', 400
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{now}] {username}: {message}'
    room_file = os.path.join(CHAT_DIR, f'{room}.txt')
    # Open in append mode and write the message as a new line.
    with open(room_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    return '', 204


@app.route('/api/chat/<room>', methods=['GET'])
def get_chat(room):
    """Return the entire chat file contents for the requested room.

    If the file does not exist yet, return an empty response (200).
    """
    room_file = os.path.join(CHAT_DIR, f'{room}.txt')
    if not os.path.exists(room_file):
        return '', 200
    with open(room_file, 'r', encoding='utf-8') as f:
        chat = f.read()
    return chat, 200


if __name__ == '__main__':
    # Run the Flask dev server. For production use a proper WSGI server.
    app.run(host='0.0.0.0', port=5000, debug=True)
