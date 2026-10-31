from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
from pathlib import Path
import json
import os

DATA_FILE = Path(os.getenv("DATA_FILE", "/var/lib/backend_data/messages.json"))

def read_messages():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

def save_message(message):
    messages = read_messages()
    messages.append({
        "message": message,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(messages, indent=2, ensure_ascii=False), encoding="utf-8")
    return messages

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/api" or self.path == "/api/":
            messages = read_messages()
            response_data = json.dumps(messages, ensure_ascii=False).encode("utf-8")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", len(response_data))
            self.end_headers()
            self.wfile.write(response_data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/" or self.path == "/api" or self.path == "/api/":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message_text = data.get("message", "").strip()
                
                if message_text:
                    save_message(message_text)
                    self.send_response(201)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b'{"status":"success"}')
                    return
            except Exception:
                pass
            
            self.send_response(400)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def run():
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    print("Backend API listening on 0.0.0.0:5000")
    httpd.serve_forever()

if __name__ == '__main__':
    run()