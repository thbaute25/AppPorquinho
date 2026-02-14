import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import database as db
import auth

# --- Configuracao da pagina ---
st.set_page_config(
    page_title="Porquinho - Finanças Pessoais",
    page_icon="🐷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS customizado ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Inicializar banco ---
db.init_db()

# --- Estado da sessao ---
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "pagina_auth" not in st.session_state:
    st.session_state.pagina_auth = "login"

MESES = [
    "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]


# =====================================================
# TELA DE LOGIN / CADASTRO
# =====================================================

def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>🐷 Porquinho</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:gray;'>Seu app de finanças pessoais</p>", unsafe_allow_html=True)
        st.divider()

        if st.session_state.pagina_auth == "login":
            st.subheader("Entrar")
            with st.form("form_login"):
                email = st.text_input("Email", placeholder="seu@email.com")
                senha = st.text_input("Senha", type="password", placeholder="Sua senha")
                submit = st.form_submit_button("Entrar", use_container_width=True)

                if submit:
                    if not email or not senha:
                        st.error("Preencha todos os campos!")
                    else:
                        usuario = auth.login(email, senha)
                        if usuario:
                            st.session_state.usuario = usuario
                            st.rerun()
                        else:
                            st.error("Email ou senha incorretos!")

            st.markdown("---")
            if st.button("Criar uma conta", use_container_width=True):
                st.session_state.pagina_auth = "cadastro"
                st.rerun()

        else:
            st.subheader("Criar Conta")
            with st.form("form_cadastro"):
                nome = st.text_input("Nome completo", placeholder="Seu nome")
                email = st.text_input("Email", placeholder="seu@email.com")
                senha = st.text_input("Senha", type="password", placeholder="Minimo 6 caracteres")
                senha2 = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")
                submit = st.form_submit_button("Criar conta", use_container_width=True)

                if submit:
                    if not nome or not email or not senha:
                        st.error("Preencha todos os campos!")
                    elif len(senha) < 6:
                        st.error("A senha deve ter no minimo 6 caracteres!")
                    elif senha != senha2:
                        st.error("As senhas nao coincidem!")
                    else:
                        usuario = auth.registrar_usuario(nome, email, senha)
                        if usuario:
                            st.session_state.usuario = usuario
                            st.success("Conta criada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Este email ja esta cadastrado!")

            st.markdown("---")
            if st.button("Ja tenho conta", use_container_width=True):
                st.session_state.pagina_auth = "login"
                st.rerun()


# =====================================================
# ABA - DASHBOARD
# =====================================================

def aba_dashboard():
    usuario_id = st.session_state.usuario["id"]
    hoje = date.today()

    col_mes, col_ano = st.columns(2)
    with col_mes:
        mes = st.selectbox("Mes", range(1, 13), index=hoje.month - 1,
                           format_func=lambda x: MESES[x - 1], key="dash_mes")
    with col_ano:
        ano = st.number_input("Ano", min_value=2020, max_value=2030, value=hoje.year, key="dash_ano")

    resumo = db.resumo_mensal(usuario_id, mes, ano)

    # Metricas principais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Receitas", f"R$ {resumo['total_receitas']:,.2f}", delta=None)
    with col2:
        st.metric("Gastos", f"R$ {resumo['total_gastos']:,.2f}", delta=None)
    with col3:
        delta_color = "normal" if resumo["saldo"] >= 0 else "inverse"
        st.metric("Saldo", f"R$ {resumo['saldo']:,.2f}",
                  delta=f"{'Positivo' if resumo['saldo'] >= 0 else 'Negativo'}",
                  delta_color=delta_color)

    st.divider()

    col_graf1, col_graf2 = st.columns(2)

    # Grafico de pizza - Gastos por categoria
    with col_graf1:
        st.subheader("Gastos por Categoria")
        if resumo["gastos_por_categoria"]:
            df_cat = pd.DataFrame(resumo["gastos_por_categoria"])
            df_cat["label"] = df_cat["icone"] + " " + df_cat["nome"]
            fig = px.pie(df_cat, values="total", names="label",
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum gasto registrado neste mes.")

    # Grafico de barras - Evolucao anual
    with col_graf2:
        st.subheader("Evolucao Anual")
        dados_anual = db.resumo_anual(usuario_id, ano)
        if dados_anual:
            df_anual = pd.DataFrame(dados_anual)
            df_anual["mes_nome"] = df_anual["mes"].apply(lambda x: MESES[int(x) - 1][:3])
            df_anual["tipo_label"] = df_anual["tipo"].apply(
                lambda x: "Receitas" if x == "receita" else "Gastos"
            )
            fig = px.bar(df_anual, x="mes_nome", y="total", color="tipo_label",
                         barmode="group",
                         color_discrete_map={"Receitas": "#2ecc71", "Gastos": "#e74c3c"})
            fig.update_layout(
                xaxis_title="", yaxis_title="Valor (R$)",
                legend_title="", margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma transacao registrada neste ano.")

    # Ultimas transacoes
    st.subheader("Ultimas Transacoes")
    transacoes = db.listar_transacoes(usuario_id, mes=mes, ano=ano)
    if transacoes:
        for t in transacoes[:10]:
            icone = t.get("categoria_icone", "📌") or "📌"
            cat = t.get("categoria_nome", "Sem categoria") or "Sem categoria"
            cor = "🔴" if t["tipo"] == "gasto" else "🟢"
            sinal = "-" if t["tipo"] == "gasto" else "+"
            st.markdown(
                f"{cor} **{t['data']}** | {icone} {cat} | {t['descricao']} | "
                f"**{sinal} R$ {t['valor']:,.2f}**"
            )
    else:
        st.info("Nenhuma transacao neste periodo.")


# =====================================================
# ABA - GASTOS
# =====================================================

def aba_gastos():
    usuario_id = st.session_state.usuario["id"]
    categorias = db.listar_categorias(usuario_id, tipo="gasto")
    cat_opcoes = {f"{c['icone']} {c['nome']}": c["id"] for c in categorias}

    st.subheader("Registrar Novo Gasto")
    with st.form("form_gasto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_input("Descricao", placeholder="Ex: Almoco no restaurante")
            categoria = st.selectbox("Categoria", list(cat_opcoes.keys()))
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
            data = st.date_input("Data", value=date.today())

        observacao = st.text_area("Observacao (opcional)", placeholder="Detalhes adicionais...", height=68)
        submit = st.form_submit_button("Registrar Gasto", use_container_width=True)

        if submit:
            if not descricao:
                st.error("Preencha a descricao!")
            else:
                db.criar_transacao(
                    descricao, valor, "gasto", cat_opcoes[categoria],
                    data.isoformat(), observacao, usuario_id
                )
                st.success(f"Gasto de R$ {valor:,.2f} registrado!")
                st.rerun()

    st.divider()

    # Listar gastos
    st.subheader("Historico de Gastos")
    hoje = date.today()
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        mes_filtro = st.selectbox("Mes", range(1, 13), index=hoje.month - 1,
                                  format_func=lambda x: MESES[x - 1], key="gasto_mes")
    with col_f2:
        ano_filtro = st.number_input("Ano", min_value=2020, max_value=2030,
                                     value=hoje.year, key="gasto_ano")

    gastos = db.listar_transacoes(usuario_id, tipo="gasto", mes=mes_filtro, ano=ano_filtro)

    if gastos:
        total = sum(g["valor"] for g in gastos)
        st.metric("Total de Gastos no Periodo", f"R$ {total:,.2f}")

        df = pd.DataFrame(gastos)
        df_display = df[["data", "descricao", "categoria_nome", "valor", "observacao"]].copy()
        df_display.columns = ["Data", "Descricao", "Categoria", "Valor (R$)", "Obs"]
        df_display["Valor (R$)"] = df_display["Valor (R$)"].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Deletar gasto
        with st.expander("Excluir um gasto"):
            opcoes_del = {f"{g['data']} - {g['descricao']} (R$ {g['valor']:,.2f})": g["id"] for g in gastos}
            gasto_del = st.selectbox("Selecione o gasto", list(opcoes_del.keys()), key="del_gasto")
            if st.button("Excluir", key="btn_del_gasto"):
                db.deletar_transacao(opcoes_del[gasto_del], usuario_id)
                st.success("Gasto excluido!")
                st.rerun()
    else:
        st.info("Nenhum gasto registrado neste periodo.")


# =====================================================
# ABA - RECEITAS
# =====================================================

def aba_receitas():
    usuario_id = st.session_state.usuario["id"]
    categorias = db.listar_categorias(usuario_id, tipo="receita")
    cat_opcoes = {f"{c['icone']} {c['nome']}": c["id"] for c in categorias}

    st.subheader("Registrar Nova Receita")
    with st.form("form_receita", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_input("Descricao", placeholder="Ex: Salario de Janeiro")
            categoria = st.selectbox("Categoria", list(cat_opcoes.keys()))
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
            data = st.date_input("Data", value=date.today())

        observacao = st.text_area("Observacao (opcional)", placeholder="Detalhes adicionais...", height=68)
        submit = st.form_submit_button("Registrar Receita", use_container_width=True)

        if submit:
            if not descricao:
                st.error("Preencha a descricao!")
            else:
                db.criar_transacao(
                    descricao, valor, "receita", cat_opcoes[categoria],
                    data.isoformat(), observacao, usuario_id
                )
                st.success(f"Receita de R$ {valor:,.2f} registrada!")
                st.rerun()

    st.divider()

    # Listar receitas
    st.subheader("Historico de Receitas")
    hoje = date.today()
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        mes_filtro = st.selectbox("Mes", range(1, 13), index=hoje.month - 1,
                                  format_func=lambda x: MESES[x - 1], key="receita_mes")
    with col_f2:
        ano_filtro = st.number_input("Ano", min_value=2020, max_value=2030,
                                     value=hoje.year, key="receita_ano")

    receitas = db.listar_transacoes(usuario_id, tipo="receita", mes=mes_filtro, ano=ano_filtro)

    if receitas:
        total = sum(r["valor"] for r in receitas)
        st.metric("Total de Receitas no Periodo", f"R$ {total:,.2f}")

        df = pd.DataFrame(receitas)
        df_display = df[["data", "descricao", "categoria_nome", "valor", "observacao"]].copy()
        df_display.columns = ["Data", "Descricao", "Categoria", "Valor (R$)", "Obs"]
        df_display["Valor (R$)"] = df_display["Valor (R$)"].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        with st.expander("Excluir uma receita"):
            opcoes_del = {f"{r['data']} - {r['descricao']} (R$ {r['valor']:,.2f})": r["id"] for r in receitas}
            rec_del = st.selectbox("Selecione a receita", list(opcoes_del.keys()), key="del_receita")
            if st.button("Excluir", key="btn_del_receita"):
                db.deletar_transacao(opcoes_del[rec_del], usuario_id)
                st.success("Receita excluida!")
                st.rerun()
    else:
        st.info("Nenhuma receita registrada neste periodo.")


# =====================================================
# ABA - INVESTIMENTOS
# =====================================================

def aba_investimentos():
    usuario_id = st.session_state.usuario["id"]
    tipos_invest = ["Renda Fixa", "Acoes", "FIIs", "Tesouro Direto", "CDB",
                    "Poupanca", "Cripto", "Outros"]

    st.subheader("Registrar Novo Investimento")
    with st.form("form_investimento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Investimento", placeholder="Ex: Tesouro Selic 2029")
            tipo = st.selectbox("Tipo", tipos_invest)
        with col2:
            valor_investido = st.number_input("Valor Investido (R$)", min_value=0.01, step=0.01, format="%.2f")
            valor_atual = st.number_input("Valor Atual (R$)", min_value=0.01, step=0.01, format="%.2f")

        data_inicio = st.date_input("Data do Investimento", value=date.today())
        observacao = st.text_area("Observacao (opcional)", height=68)
        submit = st.form_submit_button("Registrar Investimento", use_container_width=True)

        if submit:
            if not nome:
                st.error("Preencha o nome!")
            else:
                db.criar_investimento(
                    nome, tipo, valor_investido, valor_atual,
                    data_inicio.isoformat(), observacao, usuario_id
                )
                st.success(f"Investimento '{nome}' registrado!")
                st.rerun()

    st.divider()

    # Listar investimentos
    st.subheader("Meus Investimentos")
    investimentos = db.listar_investimentos(usuario_id)

    if investimentos:
        total_investido = sum(i["valor_investido"] for i in investimentos)
        total_atual = sum(i["valor_atual"] for i in investimentos)
        rendimento = total_atual - total_investido
        pct = (rendimento / total_investido * 100) if total_investido > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Investido", f"R$ {total_investido:,.2f}")
        with col2:
            st.metric("Valor Atual", f"R$ {total_atual:,.2f}")
        with col3:
            st.metric("Rendimento", f"R$ {rendimento:,.2f}",
                      delta=f"{pct:+.2f}%")

        # Grafico por tipo
        df_inv = pd.DataFrame(investimentos)
        df_tipo = df_inv.groupby("tipo")["valor_atual"].sum().reset_index()
        fig = px.pie(df_tipo, values="valor_atual", names="tipo",
                     title="Distribuicao por Tipo",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

        # Tabela
        for inv in investimentos:
            rend = inv["valor_atual"] - inv["valor_investido"]
            rend_pct = (rend / inv["valor_investido"] * 100) if inv["valor_investido"] > 0 else 0
            emoji = "📈" if rend >= 0 else "📉"

            with st.expander(f"{emoji} {inv['nome']} ({inv['tipo']}) - R$ {inv['valor_atual']:,.2f}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Investido:** R$ {inv['valor_investido']:,.2f}")
                with col2:
                    st.write(f"**Atual:** R$ {inv['valor_atual']:,.2f}")
                with col3:
                    st.write(f"**Rendimento:** R$ {rend:,.2f} ({rend_pct:+.2f}%)")

                st.write(f"**Data:** {inv['data_inicio']}")
                if inv["observacao"]:
                    st.write(f"**Obs:** {inv['observacao']}")

                col_a, col_b = st.columns(2)
                with col_a:
                    novo_valor = st.number_input(
                        "Atualizar valor atual (R$)", min_value=0.01,
                        value=inv["valor_atual"], step=0.01,
                        key=f"upd_inv_{inv['id']}"
                    )
                    if st.button("Atualizar", key=f"btn_upd_inv_{inv['id']}"):
                        db.atualizar_investimento(inv["id"], novo_valor, usuario_id)
                        st.success("Valor atualizado!")
                        st.rerun()
                with col_b:
                    if st.button("Excluir Investimento", key=f"btn_del_inv_{inv['id']}"):
                        db.deletar_investimento(inv["id"], usuario_id)
                        st.success("Investimento excluido!")
                        st.rerun()
    else:
        st.info("Nenhum investimento registrado.")


# =====================================================
# ABA - METAS
# =====================================================

def aba_metas():
    usuario_id = st.session_state.usuario["id"]

    st.subheader("Criar Nova Meta")
    with st.form("form_meta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome da Meta", placeholder="Ex: Viagem para Europa")
            valor_alvo = st.number_input("Valor Alvo (R$)", min_value=0.01, step=0.01, format="%.2f")
        with col2:
            valor_atual = st.number_input("Valor Ja Guardado (R$)", min_value=0.0, step=0.01, format="%.2f")
            prazo = st.date_input("Prazo", value=None)

        descricao = st.text_area("Descricao (opcional)", height=68)
        submit = st.form_submit_button("Criar Meta", use_container_width=True)

        if submit:
            if not nome:
                st.error("Preencha o nome da meta!")
            elif valor_alvo <= 0:
                st.error("O valor alvo deve ser maior que zero!")
            else:
                prazo_str = prazo.isoformat() if prazo else None
                db.criar_meta(nome, valor_alvo, valor_atual, prazo_str, descricao, usuario_id)
                st.success(f"Meta '{nome}' criada!")
                st.rerun()

    st.divider()

    # Listar metas
    st.subheader("Minhas Metas")
    metas = db.listar_metas(usuario_id)

    if metas:
        for meta in metas:
            progresso = (meta["valor_atual"] / meta["valor_alvo"]) if meta["valor_alvo"] > 0 else 0
            progresso = min(progresso, 1.0)
            emoji = "🎯" if progresso < 1.0 else "🏆"

            with st.expander(
                f"{emoji} {meta['nome']} - {progresso:.0%} concluida "
                f"(R$ {meta['valor_atual']:,.2f} / R$ {meta['valor_alvo']:,.2f})"
            ):
                st.progress(progresso)

                falta = meta["valor_alvo"] - meta["valor_atual"]
                if falta > 0:
                    st.write(f"**Faltam:** R$ {falta:,.2f}")
                else:
                    st.success("Meta alcancada! Parabens!")

                if meta["prazo"]:
                    st.write(f"**Prazo:** {meta['prazo']}")
                if meta["descricao"]:
                    st.write(f"**Descricao:** {meta['descricao']}")

                col_a, col_b = st.columns(2)
                with col_a:
                    novo_valor = st.number_input(
                        "Atualizar valor guardado (R$)", min_value=0.0,
                        value=meta["valor_atual"], step=0.01,
                        key=f"upd_meta_{meta['id']}"
                    )
                    if st.button("Atualizar", key=f"btn_upd_meta_{meta['id']}"):
                        db.atualizar_meta(meta["id"], novo_valor, usuario_id)
                        st.success("Meta atualizada!")
                        st.rerun()
                with col_b:
                    if st.button("Excluir Meta", key=f"btn_del_meta_{meta['id']}"):
                        db.deletar_meta(meta["id"], usuario_id)
                        st.success("Meta excluida!")
                        st.rerun()
    else:
        st.info("Nenhuma meta criada ainda. Crie sua primeira meta acima!")


# =====================================================
# APP PRINCIPAL
# =====================================================

def app_principal():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 🐷 Porquinho")
        st.markdown(f"Ola, **{st.session_state.usuario['nome']}**!")
        st.divider()
        if st.button("Sair", use_container_width=True):
            st.session_state.usuario = None
            st.rerun()

    # Abas principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "💸 Gastos",
        "💰 Receitas",
        "📈 Investimentos",
        "🎯 Metas",
    ])

    with tab1:
        aba_dashboard()
    with tab2:
        aba_gastos()
    with tab3:
        aba_receitas()
    with tab4:
        aba_investimentos()
    with tab5:
        aba_metas()


# =====================================================
# ROTEADOR
# =====================================================

if st.session_state.usuario:
    app_principal()
else:
    tela_login()
