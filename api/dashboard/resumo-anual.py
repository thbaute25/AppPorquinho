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
        ano = query.get("ano", [None])[0]

        if not ano:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Parametro ano obrigatorio"}).encode())
            return

        ano = int(ano)
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """SELECT EXTRACT(MONTH FROM data)::int as mes, tipo, COALESCE(SUM(valor), 0) as total
                   FROM transacoes
                   WHERE usuario_id = %s AND EXTRACT(YEAR FROM data) = %s
                   GROUP BY EXTRACT(MONTH FROM data), tipo
                   ORDER BY mes""",
                (usuario["id"], ano),
            )
            dados = cur.fetchall()
        finally:
            conn.close()

        result = [
            {"mes": r["mes"], "tipo": r["tipo"], "total": float(r["total"])}
            for r in dados
        ]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result, default=str).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
