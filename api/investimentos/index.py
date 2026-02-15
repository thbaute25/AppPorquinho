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
                "SELECT * FROM investimentos WHERE usuario_id = %s ORDER BY data_inicio DESC",
                (usuario["id"],),
            )
            investimentos = cur.fetchall()
        finally:
            conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(investimentos, default=str).encode())

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
        tipo = body.get("tipo", "")
        valor_investido = body.get("valor_investido")
        valor_atual = body.get("valor_atual")
        data_inicio = body.get("data_inicio")
        observacao = body.get("observacao", "")

        if not nome or not tipo or not valor_investido or not data_inicio:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Campos obrigatorios faltando"}).encode())
            return

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO investimentos (nome, tipo, valor_investido, valor_atual, data_inicio, observacao, usuario_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (nome, tipo, valor_investido, valor_atual or valor_investido, data_inicio, observacao, usuario["id"]),
            )
            new_id = cur.fetchone()["id"]
            conn.commit()
        finally:
            conn.close()

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"id": new_id, "message": "Investimento criado"}, default=str).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
