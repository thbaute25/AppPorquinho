from http.server import BaseHTTPRequestHandler
import json, sys, os
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

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM metas WHERE usuario_id = %s ORDER BY prazo ASC NULLS LAST",
                (usuario["id"],),
            )
            metas = cur.fetchall()
        finally:
            conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(metas, default=str).encode())

    def do_POST(self):
        usuario = get_usuario_from_request(self)
        if not usuario:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Nao autorizado"}).encode())
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length))

        nome = body.get("nome", "").strip()
        valor_alvo = body.get("valor_alvo")
        valor_atual = body.get("valor_atual", 0)
        prazo = body.get("prazo")
        descricao = body.get("descricao", "")

        if not nome or not valor_alvo:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Nome e valor alvo sao obrigatorios"}).encode())
            return

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO metas (nome, valor_alvo, valor_atual, prazo, descricao, usuario_id)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                (nome, valor_alvo, valor_atual, prazo, descricao, usuario["id"]),
            )
            new_id = cur.fetchone()["id"]
            conn.commit()
        finally:
            conn.close()

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"id": new_id, "message": "Meta criada"}, default=str).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
