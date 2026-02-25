# FlaskTask Chat Servers

This workspace contains two minimal Flask-based chat server examples:

- `app.py` — MySQL-backed chat API. Stores messages in a MySQL database.
- `chat_server.py` — File-backed chat API. Stores messages as text files under `chat_data/`.

Both expose the same HTTP routes used by a simple single-page client (`index.html`):

- GET `/` or `/<room>` — serves `index.html` (client UI)
- POST `/api/chat/<room>` — form fields `username` and `msg` to post a message
- GET `/api/chat/<room>` — returns chat history as plain text

Quick start (recommended: use the included virtualenv)

1. Activate virtualenv (if not already):

```bash
source newenv/bin/activate
```

2. Install dependencies (if needed):

```bash
pip install flask mysql-connector-python
```

Running the file-backed server (no DB required)

```bash
# in project root
python chat_server.py
```

Running the MySQL-backed server

1. Ensure a MySQL server is running and reachable.
2. Configure environment variables (example):

```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=secret
export MYSQL_DATABASE=chat_db
python app.py
```

`app.py` will attempt to create the `chat_db` database and the `messages`
table automatically on startup.

Example `curl` usage

Post a message:

```bash
curl -X POST -d "username=alice" -d "msg=hello" http://localhost:5000/api/chat/general
```

Get chat history:

```bash
curl http://localhost:5000/api/chat/general
```

Operational notes

- For local testing use `chat_server.py` — it stores messages in `chat_data/<room>.txt`.
- For persistence and multi-instance deployments use `app.py` with MySQL and a proper
  WSGI server (gunicorn/uwsgi) behind a reverse proxy.
- The Flask apps are configured for development (`debug=True`). Avoid this in
  production.

Security & limits

- Neither server performs authentication — do not expose to untrusted networks.
- Message length / field sizes are small and intended for demo use only.

If you'd like, I can:

- Add a `requirements.txt` and a small Dockerfile for each server.
- Add tests or CI steps to run a quick sanity check.

---
Created/edited by GitHub Copilot assistant to add documentation and inline comments.
