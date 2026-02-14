import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "porquinho.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('gasto', 'receita')),
            icone TEXT DEFAULT '📌',
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('gasto', 'receita')),
            categoria_id INTEGER,
            data TEXT NOT NULL,
            observacao TEXT,
            usuario_id INTEGER NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor_investido REAL NOT NULL,
            valor_atual REAL NOT NULL,
            data_inicio TEXT NOT NULL,
            observacao TEXT,
            usuario_id INTEGER NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor_alvo REAL NOT NULL,
            valor_atual REAL DEFAULT 0,
            prazo TEXT,
            descricao TEXT,
            usuario_id INTEGER NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()


# --- Usuarios ---

def criar_usuario(nome, email, senha_hash):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome, email, senha_hash),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def buscar_usuario_por_email(email):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


# --- Categorias ---

def criar_categorias_padrao(usuario_id):
    categorias_gasto = [
        ("Alimentacao", "🍔"), ("Transporte", "🚗"), ("Moradia", "🏠"),
        ("Saude", "💊"), ("Educacao", "📚"), ("Lazer", "🎮"),
        ("Roupas", "👕"), ("Contas", "📄"), ("Outros", "📌"),
    ]
    categorias_receita = [
        ("Salario", "💰"), ("Freelance", "💻"), ("Investimentos", "📈"),
        ("Presente", "🎁"), ("Outros", "📌"),
    ]
    conn = get_connection()
    for nome, icone in categorias_gasto:
        conn.execute(
            "INSERT INTO categorias (nome, tipo, icone, usuario_id) VALUES (?, 'gasto', ?, ?)",
            (nome, icone, usuario_id),
        )
    for nome, icone in categorias_receita:
        conn.execute(
            "INSERT INTO categorias (nome, tipo, icone, usuario_id) VALUES (?, 'receita', ?, ?)",
            (nome, icone, usuario_id),
        )
    conn.commit()
    conn.close()


def listar_categorias(usuario_id, tipo=None):
    conn = get_connection()
    if tipo:
        rows = conn.execute(
            "SELECT * FROM categorias WHERE usuario_id = ? AND tipo = ?",
            (usuario_id, tipo),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM categorias WHERE usuario_id = ?", (usuario_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Transacoes ---

def criar_transacao(descricao, valor, tipo, categoria_id, data, observacao, usuario_id):
    conn = get_connection()
    conn.execute(
        """INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data, observacao, usuario_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (descricao, valor, tipo, categoria_id, data, observacao, usuario_id),
    )
    conn.commit()
    conn.close()


def listar_transacoes(usuario_id, tipo=None, mes=None, ano=None):
    conn = get_connection()
    query = """
        SELECT t.*, c.nome as categoria_nome, c.icone as categoria_icone
        FROM transacoes t
        LEFT JOIN categorias c ON t.categoria_id = c.id
        WHERE t.usuario_id = ?
    """
    params = [usuario_id]

    if tipo:
        query += " AND t.tipo = ?"
        params.append(tipo)
    if mes and ano:
        query += " AND strftime('%m', t.data) = ? AND strftime('%Y', t.data) = ?"
        params.extend([f"{mes:02d}", str(ano)])
    elif ano:
        query += " AND strftime('%Y', t.data) = ?"
        params.append(str(ano))

    query += " ORDER BY t.data DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def deletar_transacao(transacao_id, usuario_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM transacoes WHERE id = ? AND usuario_id = ?",
        (transacao_id, usuario_id),
    )
    conn.commit()
    conn.close()


# --- Investimentos ---

def criar_investimento(nome, tipo, valor_investido, valor_atual, data_inicio, observacao, usuario_id):
    conn = get_connection()
    conn.execute(
        """INSERT INTO investimentos (nome, tipo, valor_investido, valor_atual, data_inicio, observacao, usuario_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (nome, tipo, valor_investido, valor_atual, data_inicio, observacao, usuario_id),
    )
    conn.commit()
    conn.close()


def listar_investimentos(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM investimentos WHERE usuario_id = ? ORDER BY data_inicio DESC",
        (usuario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def atualizar_investimento(investimento_id, valor_atual, usuario_id):
    conn = get_connection()
    conn.execute(
        "UPDATE investimentos SET valor_atual = ? WHERE id = ? AND usuario_id = ?",
        (valor_atual, investimento_id, usuario_id),
    )
    conn.commit()
    conn.close()


def deletar_investimento(investimento_id, usuario_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM investimentos WHERE id = ? AND usuario_id = ?",
        (investimento_id, usuario_id),
    )
    conn.commit()
    conn.close()


# --- Metas ---

def criar_meta(nome, valor_alvo, valor_atual, prazo, descricao, usuario_id):
    conn = get_connection()
    conn.execute(
        """INSERT INTO metas (nome, valor_alvo, valor_atual, prazo, descricao, usuario_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (nome, valor_alvo, valor_atual, prazo, descricao, usuario_id),
    )
    conn.commit()
    conn.close()


def listar_metas(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM metas WHERE usuario_id = ? ORDER BY prazo ASC",
        (usuario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def atualizar_meta(meta_id, valor_atual, usuario_id):
    conn = get_connection()
    conn.execute(
        "UPDATE metas SET valor_atual = ? WHERE id = ? AND usuario_id = ?",
        (valor_atual, meta_id, usuario_id),
    )
    conn.commit()
    conn.close()


def deletar_meta(meta_id, usuario_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM metas WHERE id = ? AND usuario_id = ?",
        (meta_id, usuario_id),
    )
    conn.commit()
    conn.close()


# --- Resumo para Dashboard ---

def resumo_mensal(usuario_id, mes, ano):
    conn = get_connection()
    gastos = conn.execute(
        """SELECT COALESCE(SUM(valor), 0) as total FROM transacoes
           WHERE usuario_id = ? AND tipo = 'gasto'
           AND strftime('%m', data) = ? AND strftime('%Y', data) = ?""",
        (usuario_id, f"{mes:02d}", str(ano)),
    ).fetchone()

    receitas = conn.execute(
        """SELECT COALESCE(SUM(valor), 0) as total FROM transacoes
           WHERE usuario_id = ? AND tipo = 'receita'
           AND strftime('%m', data) = ? AND strftime('%Y', data) = ?""",
        (usuario_id, f"{mes:02d}", str(ano)),
    ).fetchone()

    gastos_por_categoria = conn.execute(
        """SELECT c.nome, c.icone, COALESCE(SUM(t.valor), 0) as total
           FROM transacoes t
           JOIN categorias c ON t.categoria_id = c.id
           WHERE t.usuario_id = ? AND t.tipo = 'gasto'
           AND strftime('%m', t.data) = ? AND strftime('%Y', t.data) = ?
           GROUP BY c.nome, c.icone
           ORDER BY total DESC""",
        (usuario_id, f"{mes:02d}", str(ano)),
    ).fetchall()

    conn.close()
    return {
        "total_gastos": gastos["total"],
        "total_receitas": receitas["total"],
        "saldo": receitas["total"] - gastos["total"],
        "gastos_por_categoria": [dict(r) for r in gastos_por_categoria],
    }


def resumo_anual(usuario_id, ano):
    conn = get_connection()
    dados_mensais = conn.execute(
        """SELECT strftime('%m', data) as mes, tipo, COALESCE(SUM(valor), 0) as total
           FROM transacoes
           WHERE usuario_id = ? AND strftime('%Y', data) = ?
           GROUP BY strftime('%m', data), tipo
           ORDER BY mes""",
        (usuario_id, str(ano)),
    ).fetchall()
    conn.close()
    return [dict(r) for r in dados_mensais]
