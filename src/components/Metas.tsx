"use client";

import { useState, useEffect } from "react";
import { listarMetas, criarMeta, atualizarMeta, deletarMeta } from "@/lib/api";
import { Meta } from "@/lib/types";

export default function Metas() {
  const [metas, setMetas] = useState<Meta[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValue, setEditValue] = useState("");

  const [nome, setNome] = useState("");
  const [valorAlvo, setValorAlvo] = useState("");
  const [valorAtual, setValorAtual] = useState("");
  const [prazo, setPrazo] = useState("");
  const [descricao, setDescricao] = useState("");

  useEffect(() => {
    loadMetas();
  }, []);

  const loadMetas = async () => {
    setLoading(true);
    const m = await listarMetas();
    setMetas(m);
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (!nome) { setError("Preencha o nome da meta!"); return; }
    if (!valorAlvo || parseFloat(valorAlvo) <= 0) { setError("O valor alvo deve ser maior que zero!"); return; }

    setSubmitting(true);
    try {
      await criarMeta({
        nome,
        valor_alvo: parseFloat(valorAlvo),
        valor_atual: parseFloat(valorAtual || "0"),
        prazo: prazo || undefined,
        descricao,
      });
      setSuccess(`Meta '${nome}' criada!`);
      setNome("");
      setValorAlvo("");
      setValorAtual("");
      setPrazo("");
      setDescricao("");
      loadMetas();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao criar meta");
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (id: number) => {
    await atualizarMeta(id, parseFloat(editValue));
    setEditingId(null);
    loadMetas();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Excluir esta meta?")) return;
    await deletarMeta(id);
    loadMetas();
  };

  return (
    <div>
      <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
        <span className="text-xl">➕</span> Criar Nova Meta
      </h3>
      <form onSubmit={handleSubmit} className="form-card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Nome da Meta</label>
            <input type="text" value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Ex: Viagem para Europa" className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Valor Alvo (R$)</label>
            <input type="number" step="0.01" min="0.01" value={valorAlvo} onChange={(e) => setValorAlvo(e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Valor Ja Guardado (R$)</label>
            <input type="number" step="0.01" min="0" value={valorAtual} onChange={(e) => setValorAtual(e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Prazo</label>
            <input type="date" value={prazo} onChange={(e) => setPrazo(e.target.value)} className="input-field" />
          </div>
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-app-text-light mb-1">Descricao (opcional)</label>
          <textarea value={descricao} onChange={(e) => setDescricao(e.target.value)} className="input-field" rows={2} />
        </div>

        {error && <div className="mt-3 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>}
        {success && <div className="mt-3 p-3 bg-green-50 text-green-600 rounded-xl text-sm">{success}</div>}

        <button type="submit" className="btn-primary mt-4" disabled={submitting}>
          {submitting ? "Criando..." : "Criar Meta"}
        </button>
      </form>

      <hr className="my-6 border-none h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />

      <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
        <span className="text-xl">🎯</span> Minhas Metas
      </h3>

      {loading ? (
        <div className="text-center py-8 text-app-text-light">Carregando...</div>
      ) : metas.length > 0 ? (
        <div className="space-y-4">
          {metas.map((meta) => {
            const progresso = Number(meta.valor_alvo) > 0 ? Math.min(Number(meta.valor_atual) / Number(meta.valor_alvo), 1) : 0;
            const emoji = progresso < 1 ? "🎯" : "🏆";
            const falta = Number(meta.valor_alvo) - Number(meta.valor_atual);

            return (
              <div key={meta.id} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-bold text-app-text">
                    {emoji} {meta.nome}
                  </span>
                  <span className="text-sm text-app-text-light">
                    {(progresso * 100).toFixed(0)}% concluida
                  </span>
                </div>

                {/* Progress bar */}
                <div className="progress-bar mb-3">
                  <div className="progress-bar-fill" style={{ width: `${progresso * 100}%` }} />
                </div>

                <div className="text-sm text-app-text-light mb-2">
                  R$ {Number(meta.valor_atual).toLocaleString("pt-BR", { minimumFractionDigits: 2 })} / R$ {Number(meta.valor_alvo).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </div>

                {falta > 0 ? (
                  <div className="text-center py-2 text-sm text-app-text-light">
                    Faltam <strong className="text-primary">R$ {falta.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong> para alcancar a meta
                  </div>
                ) : (
                  <div className="text-center py-2 text-sm text-success font-semibold">Meta alcancada! Parabens!</div>
                )}

                {meta.prazo && <div className="text-xs text-app-text-light">Prazo: {meta.prazo}</div>}
                {meta.descricao && <div className="text-xs text-app-text-light">Descricao: {meta.descricao}</div>}

                <div className="flex gap-2 mt-3">
                  {editingId === meta.id ? (
                    <div className="flex gap-2 items-center">
                      <input
                        type="number"
                        step="0.01"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="input-field w-40"
                        placeholder="Novo valor"
                      />
                      <button onClick={() => handleUpdate(meta.id)} className="px-3 py-1 bg-primary text-white rounded-lg text-sm">Salvar</button>
                      <button onClick={() => setEditingId(null)} className="px-3 py-1 bg-gray-200 rounded-lg text-sm">Cancelar</button>
                    </div>
                  ) : (
                    <>
                      <button
                        onClick={() => { setEditingId(meta.id); setEditValue(String(meta.valor_atual)); }}
                        className="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100"
                      >
                        Atualizar Valor
                      </button>
                      <button
                        onClick={() => handleDelete(meta.id)}
                        className="px-3 py-1 bg-red-50 text-red-600 rounded-lg text-sm hover:bg-red-100"
                      >
                        Excluir
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <div className="text-4xl mb-2">🎯</div>
          <div>Nenhuma meta criada ainda. Defina seus objetivos!</div>
        </div>
      )}
    </div>
  );
}
