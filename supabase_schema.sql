-- ============================================
-- AppPorquinho - Schema PostgreSQL para Supabase
-- Execute este SQL no SQL Editor do Supabase
-- ============================================

-- Tabela de usuarios
CREATE TABLE usuarios (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de categorias (por usuario)
CREATE TABLE categorias (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('gasto', 'receita')),
    icone TEXT DEFAULT '📌',
    usuario_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabela de transacoes (gastos e receitas)
CREATE TABLE transacoes (
    id BIGSERIAL PRIMARY KEY,
    descricao TEXT NOT NULL,
    valor DECIMAL(12,2) NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('gasto', 'receita')),
    categoria_id BIGINT REFERENCES categorias(id) ON DELETE SET NULL,
    data DATE NOT NULL,
    observacao TEXT,
    usuario_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de investimentos
CREATE TABLE investimentos (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valor_investido DECIMAL(12,2) NOT NULL,
    valor_atual DECIMAL(12,2) NOT NULL,
    data_inicio DATE NOT NULL,
    observacao TEXT,
    usuario_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de metas
CREATE TABLE metas (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    valor_alvo DECIMAL(12,2) NOT NULL,
    valor_atual DECIMAL(12,2) DEFAULT 0,
    prazo DATE,
    descricao TEXT,
    usuario_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Indices para performance
CREATE INDEX idx_transacoes_usuario ON transacoes(usuario_id);
CREATE INDEX idx_transacoes_data ON transacoes(data);
CREATE INDEX idx_transacoes_tipo ON transacoes(tipo);
CREATE INDEX idx_categorias_usuario ON categorias(usuario_id);
CREATE INDEX idx_investimentos_usuario ON investimentos(usuario_id);
CREATE INDEX idx_metas_usuario ON metas(usuario_id);
