"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import {
  listarInvestimentos,
  criarInvestimento,
  atualizarInvestimento,
  deletarInvestimento,
} from "@/lib/api";
import { Investimento } from "@/lib/types";
import { TIPOS_INVESTIMENTO, CHART_COLORS } from "@/lib/theme";
import MetricCard from "./MetricCard";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function Investimentos() {
  const hoje = new Date();
  const [investimentos, setInvestimentos] = useState<Investimento[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValue, setEditValue] = useState("");

  const [nome, setNome] = useState("");
  const [tipo, setTipo] = useState(TIPOS_INVESTIMENTO[0]);
  const [valorInvestido, setValorInvestido] = useState("");
  const [valorAtual, setValorAtual] = useState("");
  const [dataInicio, setDataInicio] = useState(hoje.toISOString().split("T")[0]);
  const [observacao, setObservacao] = useState("");

  useEffect(() => {
    loadInvestimentos();
  }, []);

  const loadInvestimentos = async () => {
    setLoading(true);
    const inv = await listarInvestimentos();
    setInvestimentos(inv);
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (!nome) { setError("Preencha o nome!"); return; }

    setSubmitting(true);
    try {
      await criarInvestimento({
        nome,
        tipo,
        valor_investido: parseFloat(valorInvestido),
        valor_atual: parseFloat(valorAtual || valorInvestido),
        data_inicio: dataInicio,
        observacao,
      });
      setSuccess(`Investimento '${nome}' registrado!`);
      setNome("");
      setValorInvestido("");
      setValorAtual("");
      setObservacao("");
      loadInvestimentos();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao registrar investimento");
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (id: number) => {
    await atualizarInvestimento(id, parseFloat(editValue));
    setEditingId(null);
    loadInvestimentos();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Excluir este investimento?")) return;
    await deletarInvestimento(id);
    loadInvestimentos();
  };

  const totalInvestido = investimentos.reduce((s, i) => s + Number(i.valor_investido), 0);
  const totalAtual = investimentos.reduce((s, i) => s + Number(i.valor_atual), 0);
  const rendimento = totalAtual - totalInvestido;
  const pct = totalInvestido > 0 ? (rendimento / totalInvestido) * 100 : 0;

  // Agrupar por tipo para grafico
  const porTipo: Record<string, number> = {};
  investimentos.forEach((i) => {
    porTipo[i.tipo] = (porTipo[i.tipo] || 0) + Number(i.valor_atual);
  });

  return (
    <div>
      <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
        <span className="text-xl">➕</span> Registrar Novo Investimento
      </h3>
      <form onSubmit={handleSubmit} className="form-card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Nome do Investimento</label>
            <input type="text" value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Ex: Tesouro Selic 2029" className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Tipo</label>
            <select value={tipo} onChange={(e) => setTipo(e.target.value)} className="select-field">
              {TIPOS_INVESTIMENTO.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Valor Investido (R$)</label>
            <input type="number" step="0.01" min="0.01" value={valorInvestido} onChange={(e) => setValorInvestido(e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium text-app-text-light mb-1">Valor Atual (R$)</label>
            <input type="number" step="0.01" min="0.01" value={valorAtual} onChange={(e) => setValorAtual(e.target.value)} className="input-field" />
          </div>
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-app-text-light mb-1">Data do Investimento</label>
          <input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} className="input-field" />
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-app-text-light mb-1">Observacao (opcional)</label>
          <textarea value={observacao} onChange={(e) => setObservacao(e.target.value)} className="input-field" rows={2} />
        </div>

        {error && <div className="mt-3 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>}
        {success && <div className="mt-3 p-3 bg-green-50 text-green-600 rounded-xl text-sm">{success}</div>}

        <button type="submit" className="btn-primary mt-4" disabled={submitting}>
          {submitting ? "Registrando..." : "Registrar Investimento"}
        </button>
      </form>

      <hr className="my-6 border-none h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />

      <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
        <span className="text-xl">💼</span> Meus Investimentos
      </h3>

      {loading ? (
        <div className="text-center py-8 text-app-text-light">Carregando...</div>
      ) : investimentos.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <MetricCard label="Total Investido" valor={`R$ ${totalInvestido.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`} tipo="saldo" />
            <MetricCard label="Valor Atual" valor={`R$ ${totalAtual.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`} tipo={rendimento >= 0 ? "receita" : "gasto"} />
            <MetricCard label="Rendimento" valor={`R$ ${rendimento.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`} tipo={rendimento >= 0 ? "receita" : "gasto"} delta={`${pct >= 0 ? "+" : ""}${pct.toFixed(2)}%`} />
          </div>

          {/* Grafico donut */}
          {Object.keys(porTipo).length > 0 && (
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6">
              <Plot
                data={[{
                  type: "pie",
                  values: Object.values(porTipo),
                  labels: Object.keys(porTipo),
                  hole: 0.55,
                  marker: { colors: CHART_COLORS },
                }]}
                layout={{
                  margin: { t: 10, b: 10, l: 10, r: 10 },
                  paper_bgcolor: "rgba(0,0,0,0)",
                  font: { family: "Inter" },
                  height: 300,
                  legend: { orientation: "h", yanchor: "bottom", y: -0.2, xanchor: "center", x: 0.5 },
                }}
                config={{ displayModeBar: false }}
                style={{ width: "100%" }}
              />
            </div>
          )}

          {/* Lista */}
          <div className="space-y-3">
            {investimentos.map((inv) => {
              const rend = Number(inv.valor_atual) - Number(inv.valor_investido);
              const rendPct = Number(inv.valor_investido) > 0 ? (rend / Number(inv.valor_investido)) * 100 : 0;
              const emoji = rend >= 0 ? "📈" : "📉";

              return (
                <div key={inv.id} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <span className="font-bold text-app-text">{emoji} {inv.nome}</span>
                      <span className="text-app-text-light text-sm ml-2">({inv.tipo})</span>
                    </div>
                    <div className="font-bold text-app-text">
                      R$ {Number(inv.valor_atual).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-sm mb-3">
                    <div><span className="text-app-text-light">Investido:</span> <strong>R$ {Number(inv.valor_investido).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong></div>
                    <div><span className="text-app-text-light">Atual:</span> <strong>R$ {Number(inv.valor_atual).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</strong></div>
                    <div>
                      <span className="text-app-text-light">Rendimento:</span>{" "}
                      <span className={`invest-badge ${rend >= 0 ? "up" : "down"}`}>
                        R$ {rend.toLocaleString("pt-BR", { minimumFractionDigits: 2 })} ({rendPct >= 0 ? "+" : ""}{rendPct.toFixed(2)}%)
                      </span>
                    </div>
                  </div>
                  <div className="text-xs text-app-text-light mb-3">
                    Data: {inv.data_inicio} {inv.observacao && `| Obs: ${inv.observacao}`}
                  </div>
                  <div className="flex gap-2">
                    {editingId === inv.id ? (
                      <div className="flex gap-2 items-center">
                        <input
                          type="number"
                          step="0.01"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="input-field w-40"
                          placeholder="Novo valor"
                        />
                        <button onClick={() => handleUpdate(inv.id)} className="px-3 py-1 bg-primary text-white rounded-lg text-sm">Salvar</button>
                        <button onClick={() => setEditingId(null)} className="px-3 py-1 bg-gray-200 rounded-lg text-sm">Cancelar</button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => { setEditingId(inv.id); setEditValue(String(inv.valor_atual)); }}
                          className="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-sm hover:bg-blue-100"
                        >
                          Atualizar Valor
                        </button>
                        <button
                          onClick={() => handleDelete(inv.id)}
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
        </>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <div className="text-4xl mb-2">📈</div>
          <div>Nenhum investimento registrado. Comece a investir!</div>
        </div>
      )}
    </div>
  );
}
