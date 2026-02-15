"use client";

import { useAuth } from "@/contexts/AuthContext";
import Logo from "./Logo";

interface SidebarProps {
  saldo: number;
  totalInvestimentos: number;
}

export default function Sidebar({ saldo, totalInvestimentos }: SidebarProps) {
  const { usuario, logout } = useAuth();

  return (
    <div className="sidebar w-64 p-6 flex flex-col fixed left-0 top-0 h-screen overflow-y-auto">
      {/* Brand */}
      <div className="text-center pb-2">
        <Logo width={90} />
        <h1
          className="text-xl font-extrabold mt-2"
          style={{
            background: "linear-gradient(135deg, #FFB3C6, #FF6B8A)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Porquinho
        </h1>
      </div>

      {/* User */}
      <div className="text-center py-2 text-white/70 text-sm">
        Ola, <strong className="text-white">{usuario?.nome}</strong>
      </div>

      <hr className="border-white/15 my-3" />

      {/* Saldo */}
      <div className="nav-info">
        <div className="nav-info-label">Saldo Atual</div>
        <div className="nav-info-value">
          R$ {saldo.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
        </div>
      </div>

      {/* Investimentos */}
      <div className="nav-info">
        <div className="nav-info-label">Investimentos</div>
        <div className="nav-info-value">
          R$ {totalInvestimentos.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
        </div>
      </div>

      <hr className="border-white/15 my-3" />

      {/* Logout */}
      <button
        onClick={logout}
        className="mt-auto w-full py-3 rounded-xl text-sm font-medium transition-all"
        style={{
          background: "rgba(255,107,138,0.15)",
          color: "#FFB3C6",
          border: "1px solid rgba(255,107,138,0.3)",
        }}
      >
        Sair da conta
      </button>
    </div>
  );
}
