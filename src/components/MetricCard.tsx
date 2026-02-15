interface MetricCardProps {
  label: string;
  valor: string;
  tipo?: "receita" | "gasto" | "saldo";
  delta?: string;
}

export default function MetricCard({ label, valor, tipo = "saldo", delta }: MetricCardProps) {
  return (
    <div className={`metric-card ${tipo}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{valor}</div>
      {delta && <div className="metric-delta">{delta}</div>}
    </div>
  );
}
