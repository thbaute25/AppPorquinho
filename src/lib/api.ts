import {
  Usuario,
  Categoria,
  Transacao,
  Investimento,
  Meta,
  ResumoMensal,
  ResumoAnualItem,
} from "./types";

const API_BASE = "/api";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function fetchAPI<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: "Erro desconhecido" }));
    throw new Error(error.error || `Erro ${res.status}`);
  }

  return res.json();
}

// --- Auth ---

export async function login(
  email: string,
  senha: string
): Promise<{ token: string; usuario: Usuario }> {
  return fetchAPI("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, senha }),
  });
}

export async function register(
  nome: string,
  email: string,
  senha: string
): Promise<{ token: string; usuario: Usuario }> {
  return fetchAPI("/auth/register", {
    method: "POST",
    body: JSON.stringify({ nome, email, senha }),
  });
}

// --- Categorias ---

export async function listarCategorias(
  tipo?: "gasto" | "receita"
): Promise<Categoria[]> {
  const query = tipo ? `?tipo=${tipo}` : "";
  return fetchAPI(`/categorias${query}`);
}

// --- Transacoes ---

export async function listarTransacoes(params: {
  tipo?: string;
  mes?: number;
  ano?: number;
}): Promise<Transacao[]> {
  const searchParams = new URLSearchParams();
  if (params.tipo) searchParams.set("tipo", params.tipo);
  if (params.mes) searchParams.set("mes", String(params.mes));
  if (params.ano) searchParams.set("ano", String(params.ano));
  const query = searchParams.toString();
  return fetchAPI(`/transacoes${query ? `?${query}` : ""}`);
}

export async function criarTransacao(data: {
  descricao: string;
  valor: number;
  tipo: "gasto" | "receita";
  categoria_id: number;
  data: string;
  observacao?: string;
}): Promise<{ id: number }> {
  return fetchAPI("/transacoes", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deletarTransacao(id: number): Promise<void> {
  await fetchAPI(`/transacoes/${id}`, { method: "DELETE" });
}

// --- Investimentos ---

export async function listarInvestimentos(): Promise<Investimento[]> {
  return fetchAPI("/investimentos");
}

export async function criarInvestimento(data: {
  nome: string;
  tipo: string;
  valor_investido: number;
  valor_atual: number;
  data_inicio: string;
  observacao?: string;
}): Promise<{ id: number }> {
  return fetchAPI("/investimentos", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function atualizarInvestimento(
  id: number,
  valor_atual: number
): Promise<void> {
  await fetchAPI(`/investimentos/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ valor_atual }),
  });
}

export async function deletarInvestimento(id: number): Promise<void> {
  await fetchAPI(`/investimentos/${id}`, { method: "DELETE" });
}

// --- Metas ---

export async function listarMetas(): Promise<Meta[]> {
  return fetchAPI("/metas");
}

export async function criarMeta(data: {
  nome: string;
  valor_alvo: number;
  valor_atual?: number;
  prazo?: string;
  descricao?: string;
}): Promise<{ id: number }> {
  return fetchAPI("/metas", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function atualizarMeta(
  id: number,
  valor_atual: number
): Promise<void> {
  await fetchAPI(`/metas/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ valor_atual }),
  });
}

export async function deletarMeta(id: number): Promise<void> {
  await fetchAPI(`/metas/${id}`, { method: "DELETE" });
}

// --- Dashboard ---

export async function resumoMensal(
  mes: number,
  ano: number
): Promise<ResumoMensal> {
  return fetchAPI(`/dashboard/resumo-mensal?mes=${mes}&ano=${ano}`);
}

export async function resumoAnual(ano: number): Promise<ResumoAnualItem[]> {
  return fetchAPI(`/dashboard/resumo-anual?ano=${ano}`);
}
