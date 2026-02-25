import os
import sys
from pathlib import Path

# Add parent directory (project root) to Python path so we can import chat_server
sys.path.insert(0, str(Path(__file__).parent.parent))

from chat_server import app


def test_post_and_get(tmp_path, monkeypatch):
    # Redirect CHAT_DIR to a temporary directory for the test
    monkeypatch.setattr('chat_server.CHAT_DIR', str(tmp_path))
    client = app.test_client()

    # Post a message
    resp = client.post('/api/chat/testroom', data={'username': 'alice', 'msg': 'hello'})
    assert resp.status_code == 204

    # Retrieve chat history and verify content
    resp = client.get('/api/chat/testroom')
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'alice: hello' in body
