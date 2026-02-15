from http.server import BaseHTTPRequestHandler
import json, sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from _lib.db import get_connection
from _lib.auth_utils import get_usuario_from_request


class handler(BaseHTTPRequestHandler):
    def _get_id(self):
        match = re.search(r"/transacoes/(\d+)", self.path)
        return int(match.group(1)) if match else None

    def do_DELETE(self):
        usuario = get_usuario_from_request(self)
        if not usuario:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Nao autorizado"}).encode())
            return

        transacao_id = self._get_id()
        if not transacao_id:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "ID invalido"}).encode())
            return

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM transacoes WHERE id = %s AND usuario_id = %s",
                (transacao_id, usuario["id"]),
            )
            conn.commit()
        finally:
            conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Transacao excluida"}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
