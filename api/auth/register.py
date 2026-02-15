from http.server import BaseHTTPRequestHandler
import json, sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from _lib.db import get_connection
from _lib.auth_utils import hash_senha, gerar_token


# Categorias padrao criadas ao registrar usuario
CATEGORIAS_GASTO = [
    ("Alimentacao", "🍔"), ("Transporte", "🚗"), ("Moradia", "🏠"),
    ("Saude", "💊"), ("Educacao", "📚"), ("Lazer", "🎮"),
    ("Roupas", "👕"), ("Contas", "📄"), ("Outros", "📌"),
]
CATEGORIAS_RECEITA = [
    ("Salario", "💰"), ("Freelance", "💻"), ("Investimentos", "📈"),
    ("Presente", "🎁"), ("Outros", "📌"),
]


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(content_length)

        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError:
            body = {}

        nome = body.get("nome", "").strip()
        email = body.get("email", "").strip()
        senha = body.get("senha", "")

        if not nome or not email or not senha:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Nome, email e senha sao obrigatorios"}).encode())
            return

        if len(senha) < 6:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "A senha deve ter no minimo 6 caracteres"}).encode())
            return

        senha_hash = hash_senha(senha)
        conn = get_connection()
        try:
            cur = conn.cursor()
            # Criar usuario
            try:
                cur.execute(
                    "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s) RETURNING id, nome, email",
                    (nome, email, senha_hash),
                )
                usuario = cur.fetchone()
            except Exception:
                conn.rollback()
                self.send_response(409)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Este email ja esta cadastrado"}).encode())
                return

            usuario_id = usuario["id"]

            # Criar categorias padrao
            for cat_nome, icone in CATEGORIAS_GASTO:
                cur.execute(
                    "INSERT INTO categorias (nome, tipo, icone, usuario_id) VALUES (%s, 'gasto', %s, %s)",
                    (cat_nome, icone, usuario_id),
                )
            for cat_nome, icone in CATEGORIAS_RECEITA:
                cur.execute(
                    "INSERT INTO categorias (nome, tipo, icone, usuario_id) VALUES (%s, 'receita', %s, %s)",
                    (cat_nome, icone, usuario_id),
                )

            conn.commit()

            token = gerar_token(usuario)
            self.send_response(201)
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
        finally:
            conn.close()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
