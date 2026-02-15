export interface Usuario {
  id: number;
  nome: string;
  email: string;
}

export interface Categoria {
  id: number;
  nome: string;
  tipo: "gasto" | "receita";
  icone: string;
  usuario_id: number;
}

export interface Transacao {
  id: number;
  descricao: string;
  valor: number;
  tipo: "gasto" | "receita";
  categoria_id: number;
  data: string;
  observacao: string;
  usuario_id: number;
  criado_em: string;
  categoria_nome?: string;
  categoria_icone?: string;
}

export interface Investimento {
  id: number;
  nome: string;
  tipo: string;
  valor_investido: number;
  valor_atual: number;
  data_inicio: string;
  observacao: string;
  usuario_id: number;
  criado_em: string;
}

export interface Meta {
  id: number;
  nome: string;
  valor_alvo: number;
  valor_atual: number;
  prazo: string | null;
  descricao: string;
  usuario_id: number;
  criado_em: string;
}

export interface ResumoMensal {
  total_gastos: number;
  total_receitas: number;
  saldo: number;
  gastos_por_categoria: { nome: string; icone: string; total: number }[];
}

export interface ResumoAnualItem {
  mes: number;
  tipo: "gasto" | "receita";
  total: number;
}
