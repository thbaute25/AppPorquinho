import os
import json
import bcrypt
import jwt
from http.server import BaseHTTPRequestHandler


JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))


def gerar_token(usuario: dict) -> str:
    payload = {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        return None


def get_usuario_from_request(request) -> dict | None:
    """Extrai e valida o token JWT do header Authorization."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    return verificar_token(token)


def json_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def parse_body(request) -> dict:
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return {}
