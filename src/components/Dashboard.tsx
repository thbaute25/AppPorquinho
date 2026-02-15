"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import MetricCard from "./MetricCard";
import { resumoMensal, resumoAnual, listarTransacoes } from "@/lib/api";
import { ResumoMensal, ResumoAnualItem, Transacao } from "@/lib/types";
import { MESES, CHART_COLORS } from "@/lib/theme";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function Dashboard() {
  const hoje = new Date();
  const [mes, setMes] = useState(hoje.getMonth() + 1);
  const [ano, setAno] = useState(hoje.getFullYear());
  const [resumo, setResumo] = useState<ResumoMensal | null>(null);
  const [dadosAnual, setDadosAnual] = useState<ResumoAnualItem[]>([]);
  const [transacoes, setTransacoes] = useState<Transacao[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [mes, ano]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [r, a, t] = await Promise.all([
        resumoMensal(mes, ano),
        resumoAnual(ano),
        listarTransacoes({ mes, ano }),
      ]);
      setResumo(r);
      setDadosAnual(a);
      setTransacoes(t);
    } catch (err) {
      console.error("Erro ao carregar dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !resumo) {
    return <div className="text-center py-12 text-app-text-light">Carregando dashboard...</div>;
  }

  // Preparar dados do grafico de pizza
  const catLabels = resumo.gastos_por_categoria.map((c) => `${c.icone} ${c.nome}`);
  const catValues = resumo.gastos_por_categoria.map((c) => c.total);

  // Preparar dados do grafico de barras anual
  const mesesReceita = dadosAnual.filter((d) => d.tipo === "receita");
  const mesesGasto = dadosAnual.filter((d) => d.tipo === "gasto");

  return (
    <div>
      {/* Filtros */}
      <div className="flex gap-4 mb-6">
        <div>
          <label className="text-sm font-medium text-app-text-light">Mes</label>
          <select
            value={mes}
            onChange={(e) => setMes(Number(e.target.value))}
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
            value={ano}
            onChange={(e) => setAno(Number(e.target.value))}
            className="input-field block mt-1 w-28"
          />
        </div>
      </div>

      {/* Metricas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <MetricCard
          label="Receitas"
          valor={`R$ ${resumo.total_receitas.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`}
          tipo="receita"
        />
        <MetricCard
          label="Gastos"
          valor={`R$ ${resumo.total_gastos.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`}
          tipo="gasto"
        />
        <MetricCard
          label="Saldo do Mes"
          valor={`R$ ${resumo.saldo.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`}
          tipo="saldo"
          delta={resumo.saldo >= 0 ? "Positivo" : "Negativo"}
        />
      </div>

      {/* Graficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Pizza - Gastos por Categoria */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
            <span className="text-xl">🍩</span> Gastos por Categoria
          </h3>
          {catValues.length > 0 ? (
            <Plot
              data={[
                {
                  type: "pie",
                  values: catValues,
                  labels: catLabels,
                  hole: 0.55,
                  textposition: "inside",
                  textinfo: "percent+label",
                  textfont: { size: 11 },
                  marker: { colors: CHART_COLORS },
                },
              ]}
              layout={{
                showlegend: false,
                margin: { t: 10, b: 10, l: 10, r: 10 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
                font: { family: "Inter" },
                height: 350,
              }}
              config={{ displayModeBar: false }}
              style={{ width: "100%" }}
            />
          ) : (
            <div className="text-center py-12 text-gray-400">
              <div className="text-4xl mb-2">📊</div>
              <div>Nenhum gasto registrado neste mes</div>
            </div>
          )}
        </div>

        {/* Barras - Evolucao Anual */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
            <span className="text-xl">📈</span> Evolucao Anual
          </h3>
          {dadosAnual.length > 0 ? (
            <Plot
              data={[
                {
                  type: "bar",
                  x: mesesReceita.map((d) => MESES[d.mes - 1].substring(0, 3)),
                  y: mesesReceita.map((d) => d.total),
                  name: "Receitas",
                  marker: { color: "#00B894", cornerradius: 8 },
                },
                {
                  type: "bar",
                  x: mesesGasto.map((d) => MESES[d.mes - 1].substring(0, 3)),
                  y: mesesGasto.map((d) => d.total),
                  name: "Gastos",
                  marker: { color: "#FF6B6B", cornerradius: 8 },
                },
              ]}
              layout={{
                barmode: "group",
                xaxis: { title: "" },
                yaxis: {
                  title: "",
                  gridcolor: "rgba(0,0,0,0.05)",
                  zerolinecolor: "rgba(0,0,0,0.05)",
                },
                margin: { t: 10, b: 30, l: 50, r: 10 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
                font: { family: "Inter" },
                height: 350,
                legend: {
                  orientation: "h",
                  yanchor: "bottom",
                  y: 1.02,
                  xanchor: "right",
                  x: 1,
                  font: { size: 12 },
                },
              }}
              config={{ displayModeBar: false }}
              style={{ width: "100%" }}
            />
          ) : (
            <div className="text-center py-12 text-gray-400">
              <div className="text-4xl mb-2">📈</div>
              <div>Nenhuma transacao registrada neste ano</div>
            </div>
          )}
        </div>
      </div>

      {/* Ultimas Transacoes */}
      <div>
        <h3 className="text-lg font-bold text-app-text mb-4 flex items-center gap-2">
          <span className="text-xl">🕐</span> Ultimas Transacoes
        </h3>
        {transacoes.length > 0 ? (
          <div className="space-y-0">
            {transacoes.slice(0, 8).map((t) => {
              const icone = t.categoria_icone || "📌";
              const cat = t.categoria_nome || "Sem categoria";
              const sinal = t.tipo === "gasto" ? "-" : "+";
              return (
                <div key={t.id} className="tx-row">
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg ${
                        t.tipo === "gasto" ? "bg-red-50" : "bg-green-50"
                      }`}
                    >
                      {icone}
                    </div>
                    <div>
                      <div className="font-semibold text-app-text text-sm">{t.descricao}</div>
                      <div className="text-xs text-app-text-light">{cat}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold text-sm ${t.tipo === "gasto" ? "text-danger" : "text-success"}`}>
                      {sinal} R$ {Number(t.valor).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="text-xs text-app-text-light">{t.data}</div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">🐷</div>
            <div>Nenhuma transacao neste periodo. Comece registrando!</div>
          </div>
        )}
      </div>
    </div>
  );
}
