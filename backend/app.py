from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import json
import os

DATA_FILE = Path(
    os.getenv("DATA_FILE", "/var/lib/backend_data/messages.json")
)


def read_messages():
    if not DATA_FILE.exists():
        return []

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def write_messages(messages):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(messages, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def send_json(handler, status_code, data):
    response = json.dumps(data, ensure_ascii=False).encode("utf-8")

    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(response)))
    handler.end_headers()
    handler.wfile.write(response)


class SimpleAPIHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/health":
            send_json(self, 200, {
                "status": "healthy",
                "service": "backend"
            })

        elif path == "/messages":
            send_json(self, 200, read_messages())

        else:
            send_json(self, 404, {
                "error": "Endpoint not found"
            })

    def do_POST(self):
        path = urlparse(self.path).path

        if path != "/messages":
            send_json(self, 404, {
                "error": "Endpoint not found"
            })
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))

            if content_length <= 0:
                send_json(self, 400, {
                    "error": "Request body is required"
                })
                return

            data = json.loads(
                self.rfile.read(content_length).decode("utf-8")
            )

            if not isinstance(data, dict):
                raise ValueError("JSON body must be an object")

            message_text = data.get("message", "")

            if not isinstance(message_text, str) or not message_text.strip():
                send_json(self, 400, {
                    "error": "Message must not be empty"
                })
                return

            messages = read_messages()

            new_message = {
                "message": message_text.strip(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            messages.append(new_message)
            write_messages(messages)

            send_json(self, 201, {
                "status": "success",
                "data": new_message
            })

        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            send_json(self, 400, {
                "error": "Invalid request body"
            })
        except OSError:
            send_json(self, 500, {
                "error": "Failed to save message"
            })

    def do_DELETE(self):
        path = urlparse(self.path).path

        if path != "/messages":
            send_json(self, 404, {
                "error": "Endpoint not found"
            })
            return

        try:
            write_messages([])
            send_json(self, 200, {
                "status": "success",
                "message": "All messages deleted"
            })
        except OSError:
            send_json(self, 500, {
                "error": "Failed to delete messages"
            })


def run():
    server_address = ("0.0.0.0", 5000)
    httpd = HTTPServer(server_address, SimpleAPIHandler)

    print("Backend API listening on 0.0.0.0:5000")
    httpd.serve_forever()


if __name__ == "__main__":
    run()