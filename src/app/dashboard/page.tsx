"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { resumoMensal, listarInvestimentos } from "@/lib/api";
import Sidebar from "@/components/Sidebar";
import Dashboard from "@/components/Dashboard";
import Gastos from "@/components/Gastos";
import Receitas from "@/components/Receitas";
import Investimentos from "@/components/Investimentos";
import Metas from "@/components/Metas";

const TABS = [
  { id: "dashboard", label: "📊 Dashboard" },
  { id: "gastos", label: "💸 Gastos" },
  { id: "receitas", label: "💰 Receitas" },
  { id: "investimentos", label: "📈 Investimentos" },
  { id: "metas", label: "🎯 Metas" },
];

export default function DashboardPage() {
  const { usuario, isLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [saldo, setSaldo] = useState(0);
  const [totalInvestimentos, setTotalInvestimentos] = useState(0);

  useEffect(() => {
    if (!isLoading && !usuario) {
      router.push("/");
    }
  }, [isLoading, usuario, router]);

  useEffect(() => {
    if (usuario) {
      loadSidebarData();
    }
  }, [usuario, activeTab]);

  const loadSidebarData = async () => {
    try {
      const hoje = new Date();
      const [resumo, investimentos] = await Promise.all([
        resumoMensal(hoje.getMonth() + 1, hoje.getFullYear()),
        listarInvestimentos(),
      ]);
      setSaldo(resumo.saldo);
      setTotalInvestimentos(
        investimentos.reduce((s, i) => s + Number(i.valor_atual), 0)
      );
    } catch (err) {
      console.error("Erro ao carregar dados da sidebar:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-app-text-light">Carregando...</div>
      </div>
    );
  }

  if (!usuario) return null;

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <Sidebar saldo={saldo} totalInvestimentos={totalInvestimentos} />

      {/* Main Content */}
      <div className="ml-64 flex-1 p-8">
        {/* Tabs */}
        <div className="bg-white rounded-2xl p-1.5 shadow-sm border border-gray-100 inline-flex gap-1 mb-8">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? "tab-active"
                  : "text-app-text-light hover:bg-gray-50"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "dashboard" && <Dashboard />}
        {activeTab === "gastos" && <Gastos />}
        {activeTab === "receitas" && <Receitas />}
        {activeTab === "investimentos" && <Investimentos />}
        {activeTab === "metas" && <Metas />}
      </div>
    </div>
  );
}
