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
        mes = query.get("mes", [None])[0]
        ano = query.get("ano", [None])[0]

        conn = get_connection()
        try:
            cur = conn.cursor()
            sql = """
                SELECT t.*, c.nome as categoria_nome, c.icone as categoria_icone
                FROM transacoes t
                LEFT JOIN categorias c ON t.categoria_id = c.id
                WHERE t.usuario_id = %s
            """
            params = [usuario["id"]]

            if tipo:
                sql += " AND t.tipo = %s"
                params.append(tipo)
            if mes and ano:
                sql += " AND EXTRACT(MONTH FROM t.data) = %s AND EXTRACT(YEAR FROM t.data) = %s"
                params.extend([int(mes), int(ano)])
            elif ano:
                sql += " AND EXTRACT(YEAR FROM t.data) = %s"
                params.append(int(ano))

            sql += " ORDER BY t.data DESC"
            cur.execute(sql, params)
            transacoes = cur.fetchall()
        finally:
            conn.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(transacoes, default=str).encode())

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

        descricao = body.get("descricao", "").strip()
        valor = body.get("valor")
        tipo = body.get("tipo")
        categoria_id = body.get("categoria_id")
        data = body.get("data")
        observacao = body.get("observacao", "")

        if not descricao or not valor or not tipo or not data:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Campos obrigatorios faltando"}).encode())
            return

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data, observacao, usuario_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (descricao, valor, tipo, categoria_id, data, observacao, usuario["id"]),
            )
            new_id = cur.fetchone()["id"]
            conn.commit()
        finally:
            conn.close()

        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"id": new_id, "message": "Transacao criada"}, default=str).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
