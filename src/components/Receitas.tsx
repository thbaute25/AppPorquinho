"use client";

import { useState, useEffect } from "react";
import { listarCategorias, listarTransacoes, criarTransacao, deletarTransacao } from "@/lib/api";
import { Categoria, Transacao } from "@/lib/types";
import { MESES } from "@/lib/theme";
import MetricCard from "./MetricCard";

export default function Receitas() {
  const hoje = new Date();
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [receitas, setReceitas] = useState<Transacao[]>([]);
  const [mesFiltro, setMesFiltro] = useState(hoje.getMonth() + 1);
  const [anoFiltro, setAnoFiltro] = useState(hoje.getFullYear());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [descricao, setDescricao] = useState("");
  const [valor, setValor] = useState("");
  const [categoriaId, setCategoriaId] = useState<number>(0);
  const [data, setData] = useState(hoje.toISOString().split("T")[0]);
  const [observacao, setObservacao] = useState("");

  useEffect(() => {
    loadCategorias();
  }, []);

  useEffect(() => {
    loadReceitas();
  }, [mesFiltro, anoFiltro]);

  const loadCategorias = async () => {
    const cats = await listarCategorias("receita");
    setCategorias(cats);
    if (cats.length > 0) setCategoriaId(cats[0].id);
  };

  const loadReceitas = async () => {
    setLoading(true);
    const r = await listarTransacoes({ tipo: "receita", mes: mesFiltro, ano: anoFiltro });
    setReceitas(r);
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (!descricao) { setError("Preencha a descricao!"); return; }

    setSubmitting(true);
    try {
      await criarTransacao({
        descricao,
        valor: parseFloat(valor),
        tipo: "receita",
        categoria_id: categoriaId,
        data,
        observacao,
      });
      setSuccess(`Receita de R$ ${parseFloat(valor).toFixed(2)} registrada!`);
      setDescricao("");
      setValor("");
      setObservacao("");
      loadReceitas();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao registrar receita");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Excluir esta receita?")) return;
    await deletarTransacao(id);
    loadReceitas();
  };

  const total = receitas.reduce((sum, r) => sum + Number(r.valor), 0);

  return (
    <div>
      <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
        <span className="text-xl">➕</span> Registrar Nova Receita
      </h3>
      <form onSubmit={handleSubmit} className="form-card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Descricao</label>
            <input
              type="text"
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              placeholder="Ex: Salario de Janeiro"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Valor (R$)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={valor}
              onChange={(e) => setValor(e.target.value)}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Categoria</label>
            <select
              value={categoriaId}
              onChange={(e) => setCategoriaId(Number(e.target.value))}
              className="select-field"
            >
              {categorias.map((c) => (
                <option key={c.id} value={c.id}>{c.icone} {c.nome}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Data</label>
            <input
              type="date"
              value={data}
              onChange={(e) => setData(e.target.value)}
              className="input-field"
            />
          </div>
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-app-text-light mb-1">Observacao (opcional)</label>
          <textarea
            value={observacao}
            onChange={(e) => setObservacao(e.target.value)}
            placeholder="Detalhes adicionais..."
            className="input-field"
            rows={2}
          />
        </div>

        {error && <div className="mt-3 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>}
        {success && <div className="mt-3 p-3 bg-green-50 text-green-600 rounded-xl text-sm">{success}</div>}

        <button type="submit" className="btn-primary mt-4" disabled={submitting}>
          {submitting ? "Registrando..." : "Registrar Receita"}
        </button>
      </form>

      <hr className="my-6 border-none h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />

      <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
        <span className="text-xl">📋</span> Historico de Receitas
      </h3>

      <div className="flex gap-4 mb-4">
        <div>
          <label className="text-sm font-medium text-app-text-light">Mes</label>
          <select
            value={mesFiltro}
            onChange={(e) => setMesFiltro(Number(e.target.value))}
            className="select-field block mt-1"
          >
            {MESES.map((m, i) => (
              <option key={i} value={i + 1}>{m}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-sm font-medium text-app-text-light">Ano</label>
          <input
            type="number"
            min={2020}
            max={2030}
            value={anoFiltro}
            onChange={(e) => setAnoFiltro(Number(e.target.value))}
            className="input-field block mt-1 w-28"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-app-text-light">Carregando...</div>
      ) : receitas.length > 0 ? (
        <>
          <div className="mb-4">
            <MetricCard
              label="Total de Receitas no Periodo"
              valor={`R$ ${total.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`}
              tipo="receita"
            />
          </div>
          <div className="space-y-0">
            {receitas.map((r) => (
              <div key={r.id} className="tx-row group">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg bg-green-50">
                    {r.categoria_icone || "📌"}
                  </div>
                  <div>
                    <div className="font-semibold text-app-text text-sm">{r.descricao}</div>
                    <div className="text-xs text-app-text-light">{r.categoria_nome || "Sem categoria"}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className="font-bold text-sm text-success">
                      + R$ {Number(r.valor).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="text-xs text-app-text-light">{r.data}</div>
                  </div>
                  <button
                    onClick={() => handleDelete(r.id)}
                    className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 text-sm transition-opacity"
                    title="Excluir"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <div className="text-4xl mb-2">💰</div>
          <div>Nenhuma receita registrada neste periodo</div>
        </div>
      )}
    </div>
  );
}
