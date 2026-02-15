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
        mes = query.get("mes", [None])[0]
        ano = query.get("ano", [None])[0]

        if not mes or not ano:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Parametros mes e ano sao obrigatorios"}).encode())
            return

        mes = int(mes)
        ano = int(ano)
        usuario_id = usuario["id"]

        conn = get_connection()
        try:
            cur = conn.cursor()

            # Total de gastos
            cur.execute(
                """SELECT COALESCE(SUM(valor), 0) as total FROM transacoes
                   WHERE usuario_id = %s AND tipo = 'gasto'
                   AND EXTRACT(MONTH FROM data) = %s AND EXTRACT(YEAR FROM data) = %s""",
                (usuario_id, mes, ano),
            )
            total_gastos = float(cur.fetchone()["total"])

            # Total de receitas
            cur.execute(
                """SELECT COALESCE(SUM(valor), 0) as total FROM transacoes
                   WHERE usuario_id = %s AND tipo = 'receita'
                   AND EXTRACT(MONTH FROM data) = %s AND EXTRACT(YEAR FROM data) = %s""",
                (usuario_id, mes, ano),
            )
            total_receitas = float(cur.fetchone()["total"])

            # Gastos por categoria
            cur.execute(
                """SELECT c.nome, c.icone, COALESCE(SUM(t.valor), 0) as total
                   FROM transacoes t
                   JOIN categorias c ON t.categoria_id = c.id
                   WHERE t.usuario_id = %s AND t.tipo = 'gasto'
                   AND EXTRACT(MONTH FROM t.data) = %s AND EXTRACT(YEAR FROM t.data) = %s
                   GROUP BY c.nome, c.icone
                   ORDER BY total DESC""",
                (usuario_id, mes, ano),
            )
            gastos_por_categoria = cur.fetchall()
        finally:
            conn.close()

        result = {
            "total_gastos": total_gastos,
            "total_receitas": total_receitas,
            "saldo": total_receitas - total_gastos,
            "gastos_por_categoria": [
                {"nome": r["nome"], "icone": r["icone"], "total": float(r["total"])}
                for r in gastos_por_categoria
            ],
        }

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
