from http.server import BaseHTTPRequestHandler
import json, sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from _lib.db import get_connection
from _lib.auth_utils import get_usuario_from_request


class handler(BaseHTTPRequestHandler):
    def _get_id(self):
        match = re.search(r"/investimentos/(\d+)", self.path)
        return int(match.group(1)) if match else None

    def do_PATCH(self):
        usuario = get_usuario_from_request(self)
        if not usuario:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Nao autorizado"}).encode())
            return

        investimento_id = self._get_id()
        if not investimento_id:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "ID invalido"}).encode())
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length))
        valor_atual = body.get("valor_atual")

        if valor_atual is None:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "valor_atual obrigatorio"}).encode())
            return

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE investimentos SET valor_atual = %s WHERE id = %s AND usuario_id = %s",
                (valor_atual, investimento_id, usuario["id"]),
            )
            conn.commit()
        finally:
            conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Investimento atualizado"}).encode())

    def do_DELETE(self):
        usuario = get_usuario_from_request(self)
        if not usuario:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Nao autorizado"}).encode())
            return

        investimento_id = self._get_id()
        if not investimento_id:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "ID invalido"}).encode())
            return

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM investimentos WHERE id = %s AND usuario_id = %s",
                (investimento_id, usuario["id"]),
            )
            conn.commit()
        finally:
            conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Investimento excluido"}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
