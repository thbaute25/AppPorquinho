from http.server import BaseHTTPRequestHandler
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from _lib.db import get_connection
from _lib.auth_utils import verificar_senha, gerar_token, json_response, parse_body


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(content_length)

        import json
        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError:
            body = {}

        email = body.get("email", "").strip()
        senha = body.get("senha", "")

        if not email or not senha:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Email e senha sao obrigatorios"}).encode())
            return

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            usuario = cur.fetchone()
        finally:
            conn.close()

        if not usuario or not verificar_senha(senha, usuario["senha_hash"]):
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Email ou senha incorretos"}).encode())
            return

        token = gerar_token(usuario)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "token": token,
            "usuario": {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
            }
        }, default=str).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
