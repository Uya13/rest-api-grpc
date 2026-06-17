import base64
import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


JWT_SECRET = os.getenv("JWT_SECRET", "practice-secret")
PORT = int(os.getenv("PORT", "5001"))

TODOS = {
    "student": [
        {"id": 1, "title": "Проверить REST-запрос через Nginx", "completed": False},
        {"id": 2, "title": "Передать JWT в Authorization header", "completed": False},
    ],
    "admin": [
        {"id": 1, "title": "Проверить маршрутизацию API Gateway", "completed": True},
    ],
}


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length == 0:
        return {}

    return json.loads(handler.rfile.read(length).decode("utf-8"))


def base64url_decode(value):
    value += "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value.encode())


def validate_token(token):
    try:
        header, payload, signature = token.split(".")
        expected = hmac.new(
            JWT_SECRET.encode(),
            f"{header}.{payload}".encode(),
            hashlib.sha256,
        ).digest()

        expected_signature = base64.urlsafe_b64encode(expected).rstrip(b"=").decode()
        if not hmac.compare_digest(signature, expected_signature):
            return None

        claims = json.loads(base64url_decode(payload))
        if claims.get("exp", 0) < int(time.time()):
            return None

        return claims
    except Exception:
        return None


def current_user(handler):
    auth = handler.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None

    return validate_token(auth.removeprefix("Bearer ").strip())


class TodoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            json_response(self, 200, {"service": "todo-service", "status": "ok"})
            return

        if self.path == "/todos":
            claims = current_user(self)
            if claims is None:
                json_response(self, 401, {"error": "Valid bearer token is required"})
                return

            username = claims["sub"]
            json_response(self, 200, {
                "user": username,
                "role": claims["role"],
                "items": TODOS.get(username, []),
            })
            return

        json_response(self, 404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/todos":
            claims = current_user(self)
            if claims is None:
                json_response(self, 401, {"error": "Valid bearer token is required"})
                return

            data = read_json(self)
            title = data.get("title", "").strip()
            if not title:
                json_response(self, 400, {"error": "Title is required"})
                return

            username = claims["sub"]
            user_todos = TODOS.setdefault(username, [])
            todo = {"id": len(user_todos) + 1, "title": title, "completed": False}
            user_todos.append(todo)
            json_response(self, 201, todo)
            return

        json_response(self, 404, {"error": "Not found"})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), TodoHandler)
    print(f"todo-service started on port {PORT}", flush=True)
    server.serve_forever()
