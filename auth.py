import bcrypt
import database as db


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha, senha_hash):
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))


def registrar_usuario(nome, email, senha):
    senha_hash = hash_senha(senha)
    sucesso = db.criar_usuario(nome, email, senha_hash)
    if sucesso:
        usuario = db.buscar_usuario_por_email(email)
        db.criar_categorias_padrao(usuario["id"])
        return usuario
    return None


def login(email, senha):
    usuario = db.buscar_usuario_por_email(email)
    if usuario and verificar_senha(senha, usuario["senha_hash"]):
        return usuario
    return None
