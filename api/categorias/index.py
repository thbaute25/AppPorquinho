from http.server import BaseHTTPRequestHandler
import json, sys, os
from urllib.parse import urlparse, parse_qs
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from _lib.db import get_connection
from _lib.auth_utils import get_usuario_from_request


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        usuario = get_usuario_from_request(self)
        if not usuario:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Nao autorizado"}).encode())
            return

        query = parse_qs(urlparse(self.path).query)
        tipo = query.get("tipo", [None])[0]

        conn = get_connection()
        try:
            cur = conn.cursor()
            if tipo:
                cur.execute(
                    "SELECT * FROM categorias WHERE usuario_id = %s AND tipo = %s ORDER BY nome",
                    (usuario["id"], tipo),
                )
            else:
                cur.execute(
                    "SELECT * FROM categorias WHERE usuario_id = %s ORDER BY tipo, nome",
                    (usuario["id"],),
                )
            categorias = cur.fetchall()
        finally:
            conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(categorias, default=str).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
