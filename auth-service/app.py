import base64
import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


JWT_SECRET = os.getenv("JWT_SECRET", "practice-secret")
PORT = int(os.getenv("PORT", "5000"))

USERS = {
    "student": {
        "password_hash": hashlib.sha256("student123".encode()).hexdigest(),
        "role": "user",
    },
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
    },
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


def base64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def create_token(username, role):
    header = base64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = base64url(json.dumps({
        "sub": username,
        "role": role,
        "exp": int(time.time()) + 3600,
    }).encode())
    signature = hmac.new(
        JWT_SECRET.encode(),
        f"{header}.{payload}".encode(),
        hashlib.sha256,
    ).digest()
    return f"{header}.{payload}.{base64url(signature)}"


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            json_response(self, 200, {"service": "auth-service", "status": "ok"})
            return

        json_response(self, 404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/login":
            data = read_json(self)
            username = data.get("username", "")
            password = data.get("password", "")
            user = USERS.get(username)

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user is None or not hmac.compare_digest(user["password_hash"], password_hash):
                json_response(self, 401, {"error": "Invalid username or password"})
                return

            json_response(self, 200, {
                "token": create_token(username, user["role"]),
                "username": username,
                "role": user["role"],
            })
            return

        json_response(self, 404, {"error": "Not found"})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), AuthHandler)
    print(f"auth-service started on port {PORT}", flush=True)
    server.serve_forever()
