import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import database as db
import auth
from logo import get_logo_html, get_logo_sidebar_html

# --- Configuracao da pagina ---
st.set_page_config(
    page_title="Porquinho - Financas Pessoais",
    page_icon="🐷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Paleta de cores ---
COLORS = {
    "primary": "#FF6B8A",
    "primary_dark": "#E8527A",
    "primary_light": "#FFB3C6",
    "secondary": "#6C5CE7",
    "accent": "#00D2D3",
    "success": "#00B894",
    "danger": "#FF6B6B",
    "warning": "#FDCB6E",
    "bg": "#FAFAFA",
    "card": "#FFFFFF",
    "text": "#1A1A2E",
    "text_light": "#6B7280",
    "border": "#F3E8FF",
}

# --- CSS Moderno ---
st.markdown(f"""
<style>
    /* ===== Google Fonts ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ===== Reset & Base ===== */
    *, *::before, *::after {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }}

    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
        color: white;
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: white !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15) !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: rgba(255,107,138,0.15) !important;
        color: #FFB3C6 !important;
        border: 1px solid rgba(255,107,138,0.3) !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(255,107,138,0.3) !important;
        color: white !important;
        transform: translateY(-1px) !important;
    }}

    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {{
        background: white;
        border-radius: 16px;
        padding: 6px;
        gap: 4px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #F0F0F5;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        color: {COLORS['text_light']} !important;
        transition: all 0.3s ease !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255,107,138,0.3) !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* ===== Metricas ===== */
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.05);
        border: 1px solid #F0F0F5;
        transition: all 0.3s ease;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: {COLORS['text_light']} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: {COLORS['text']} !important;
    }}

    /* ===== Botoes ===== */
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        letter-spacing: 0.3px !important;
    }}
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(255,107,138,0.3) !important;
        transition: all 0.3s ease !important;
    }}
    .stFormSubmitButton > button:hover {{
        box-shadow: 0 6px 20px rgba(255,107,138,0.4) !important;
        transform: translateY(-2px) !important;
    }}

    /* ===== Inputs ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-radius: 12px !important;
        border: 2px solid #E8E8F0 !important;
        padding: 0.7rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 3px rgba(255,107,138,0.15) !important;
    }}

    .stSelectbox > div > div {{
        border-radius: 12px !important;
    }}

    /* ===== Cards / Containers ===== */
    .stExpander {{
        background: white !important;
        border-radius: 16px !important;
        border: 1px solid #F0F0F5 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
        overflow: hidden;
    }}
    .stExpander summary {{
        font-weight: 600 !important;
    }}

    /* ===== Forms ===== */
    [data-testid="stForm"] {{
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #F0F0F5;
    }}

    /* ===== Dataframe ===== */
    .stDataFrame {{
        border-radius: 16px !important;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }}

    /* ===== Divider ===== */
    hr {{
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #E8E8F0, transparent) !important;
        margin: 2rem 0 !important;
    }}

    /* ===== Progress ===== */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']}) !important;
        border-radius: 10px !important;
    }}
    .stProgress > div > div {{
        background: #F0F0F5 !important;
        border-radius: 10px !important;
    }}

    /* ===== Success / Error / Info ===== */
    .stAlert {{
        border-radius: 12px !important;
        border: none !important;
    }}

    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['primary_light']};
        border-radius: 10px;
    }}

    /* ===== Login Page Custom ===== */
    .login-container {{
        background: white;
        border-radius: 24px;
        padding: 3rem 2.5rem;
        box-shadow: 0 20px 60px rgba(255,107,138,0.12), 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid rgba(255,107,138,0.1);
        text-align: center;
        max-width: 420px;
        margin: 0 auto;
    }}
    .login-title {{
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0 0.2rem 0;
    }}
    .login-subtitle {{
        color: {COLORS['text_light']};
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 1rem;
    }}

    /* ===== Sidebar branding ===== */
    .sidebar-brand {{
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }}
    .sidebar-brand-name {{
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFB3C6, #FF6B8A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0 0;
    }}
    .sidebar-user {{
        text-align: center;
        padding: 0.5rem 0;
        color: rgba(255,255,255,0.7);
        font-size: 0.95rem;
    }}
    .sidebar-user strong {{
        color: white;
    }}

    /* ===== Custom metric cards ===== */
    .metric-card {{
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        border: none;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
    }}
    .metric-card.receita {{
        background: linear-gradient(135deg, #00B894 0%, #00CEC9 100%);
        box-shadow: 0 8px 25px rgba(0,184,148,0.25);
    }}
    .metric-card.gasto {{
        background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%);
        box-shadow: 0 8px 25px rgba(255,107,107,0.25);
    }}
    .metric-card.saldo {{
        background: linear-gradient(135deg, {COLORS['secondary']} 0%, #A29BFE 100%);
        box-shadow: 0 8px 25px rgba(108,92,231,0.25);
    }}
    .metric-card .metric-label {{
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255,255,255,0.85);
        margin-bottom: 0.5rem;
    }}
    .metric-card .metric-value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
    }}
    .metric-card .metric-delta {{
        font-size: 0.85rem;
        font-weight: 500;
        color: rgba(255,255,255,0.8);
        margin-top: 0.3rem;
    }}

    /* ===== Section headers ===== */
    .section-header {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {COLORS['text']};
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .section-header .header-icon {{
        font-size: 1.5rem;
    }}

    /* ===== Transaction row ===== */
    .tx-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.2rem;
        background: white;
        border-radius: 14px;
        margin-bottom: 0.6rem;
        border: 1px solid #F0F0F5;
        transition: all 0.2s ease;
    }}
    .tx-row:hover {{
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        transform: translateX(4px);
    }}
    .tx-left {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    .tx-icon {{
        width: 42px;
        height: 42px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }}
    .tx-icon.gasto {{ background: rgba(255,107,107,0.12); }}
    .tx-icon.receita {{ background: rgba(0,184,148,0.12); }}
    .tx-desc {{
        font-weight: 600;
        color: {COLORS['text']};
        font-size: 0.95rem;
    }}
    .tx-cat {{
        font-size: 0.8rem;
        color: {COLORS['text_light']};
    }}
    .tx-right {{
        text-align: right;
    }}
    .tx-valor {{
        font-weight: 700;
        font-size: 1.05rem;
    }}
    .tx-valor.gasto {{ color: #FF6B6B; }}
    .tx-valor.receita {{ color: #00B894; }}
    .tx-data {{
        font-size: 0.78rem;
        color: {COLORS['text_light']};
    }}

    /* ===== Invest card ===== */
    .invest-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    .invest-badge.up {{ background: rgba(0,184,148,0.12); color: #00B894; }}
    .invest-badge.down {{ background: rgba(255,107,107,0.12); color: #FF6B6B; }}

    /* ===== Sidebar nav items ===== */
    .nav-info {{
        background: rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    .nav-info-label {{
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255,255,255,0.4);
        margin-bottom: 0.3rem;
    }}
    .nav-info-value {{
        font-size: 1.1rem;
        font-weight: 700;
        color: white;
    }}
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
# HELPERS DE VISUAL
# =====================================================

def metric_card(label, valor, tipo="saldo"):
    """Card de metrica customizado com gradiente"""
    st.markdown(f"""
        <div class="metric-card {tipo}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{valor}</div>
        </div>
    """, unsafe_allow_html=True)


def metric_card_delta(label, valor, delta_text, tipo="saldo"):
    """Card de metrica com indicador delta"""
    st.markdown(f"""
        <div class="metric-card {tipo}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{valor}</div>
            <div class="metric-delta">{delta_text}</div>
        </div>
    """, unsafe_allow_html=True)


def section_header(icon, text):
    st.markdown(f'<div class="section-header"><span class="header-icon">{icon}</span> {text}</div>',
                unsafe_allow_html=True)


def transacao_row(data, descricao, categoria, icone_cat, valor, tipo):
    sinal = "-" if tipo == "gasto" else "+"
    st.markdown(f"""
        <div class="tx-row">
            <div class="tx-left">
                <div class="tx-icon {tipo}">{icone_cat}</div>
                <div>
                    <div class="tx-desc">{descricao}</div>
                    <div class="tx-cat">{categoria}</div>
                </div>
            </div>
            <div class="tx-right">
                <div class="tx-valor {tipo}">{sinal} R$ {valor:,.2f}</div>
                <div class="tx-data">{data}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# =====================================================
# TELA DE LOGIN / CADASTRO
# =====================================================

def tela_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"""
            <div class="login-container">
                {get_logo_html(130)}
                <div class="login-title">Porquinho</div>
                <div class="login-subtitle">Suas financas de um jeito simples</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.pagina_auth == "login":
            with st.form("form_login"):
                st.markdown("##### Entrar na sua conta")
                email = st.text_input("Email", placeholder="seu@email.com", label_visibility="collapsed")
                senha = st.text_input("Senha", type="password", placeholder="Sua senha", label_visibility="collapsed")
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

            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("Criar uma conta", use_container_width=True):
                    st.session_state.pagina_auth = "cadastro"
                    st.rerun()

        else:
            with st.form("form_cadastro"):
                st.markdown("##### Criar nova conta")
                nome = st.text_input("Nome", placeholder="Seu nome completo", label_visibility="collapsed")
                email = st.text_input("Email", placeholder="seu@email.com", label_visibility="collapsed")
                senha = st.text_input("Senha", type="password", placeholder="Minimo 6 caracteres", label_visibility="collapsed")
                senha2 = st.text_input("Confirmar", type="password", placeholder="Repita a senha", label_visibility="collapsed")
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

            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("Ja tenho conta", use_container_width=True):
                    st.session_state.pagina_auth = "login"
                    st.rerun()


# =====================================================
# ABA - DASHBOARD
# =====================================================

def aba_dashboard():
    usuario_id = st.session_state.usuario["id"]
    hoje = date.today()

    col_mes, col_ano, col_spacer = st.columns([1, 1, 2])
    with col_mes:
        mes = st.selectbox("Mes", range(1, 13), index=hoje.month - 1,
                           format_func=lambda x: MESES[x - 1], key="dash_mes")
    with col_ano:
        ano = st.number_input("Ano", min_value=2020, max_value=2030, value=hoje.year, key="dash_ano")

    resumo = db.resumo_mensal(usuario_id, mes, ano)

    st.markdown("<br>", unsafe_allow_html=True)

    # Metricas com cards customizados
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Receitas", f"R$ {resumo['total_receitas']:,.2f}", "receita")
    with col2:
        metric_card("Gastos", f"R$ {resumo['total_gastos']:,.2f}", "gasto")
    with col3:
        delta = "Positivo" if resumo["saldo"] >= 0 else "Negativo"
        metric_card_delta("Saldo do Mes", f"R$ {resumo['saldo']:,.2f}", delta, "saldo")

    st.markdown("<br>", unsafe_allow_html=True)

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        section_header("🍩", "Gastos por Categoria")
        if resumo["gastos_por_categoria"]:
            df_cat = pd.DataFrame(resumo["gastos_por_categoria"])
            df_cat["label"] = df_cat["icone"] + " " + df_cat["nome"]
            fig = px.pie(df_cat, values="total", names="label", hole=0.55,
                                    color_discrete_sequence=[
                                        "#FF6B8A", "#6C5CE7", "#00D2D3", "#FDCB6E",
                                        "#00B894", "#E17055", "#A29BFE", "#FD79A8", "#55A3F5"
                                    ])
            fig.update_traces(textposition="inside", textinfo="percent+label",
                              textfont_size=11)
            fig.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
                <div style="text-align:center; padding:3rem; color:#9CA3AF;">
                    <div style="font-size:3rem; margin-bottom:0.5rem;">📊</div>
                    <div>Nenhum gasto registrado neste mes</div>
                </div>
            """, unsafe_allow_html=True)

    with col_graf2:
        section_header("📈", "Evolucao Anual")
        dados_anual = db.resumo_anual(usuario_id, ano)
        if dados_anual:
            df_anual = pd.DataFrame(dados_anual)
            df_anual["mes_nome"] = df_anual["mes"].apply(lambda x: MESES[int(x) - 1][:3])
            df_anual["tipo_label"] = df_anual["tipo"].apply(
                lambda x: "Receitas" if x == "receita" else "Gastos"
            )
            fig = px.bar(df_anual, x="mes_nome", y="total", color="tipo_label",
                         barmode="group",
                         color_discrete_map={"Receitas": "#00B894", "Gastos": "#FF6B6B"})
            fig.update_layout(
                xaxis_title="", yaxis_title="",
                legend_title="",
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                height=350,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=12)
                ),
                yaxis=dict(gridcolor="rgba(0,0,0,0.05)", zerolinecolor="rgba(0,0,0,0.05)"),
            )
            fig.update_traces(marker_cornerradius=8)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
                <div style="text-align:center; padding:3rem; color:#9CA3AF;">
                    <div style="font-size:3rem; margin-bottom:0.5rem;">📈</div>
                    <div>Nenhuma transacao registrada neste ano</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Ultimas transacoes
    section_header("🕐", "Ultimas Transacoes")
    transacoes = db.listar_transacoes(usuario_id, mes=mes, ano=ano)
    if transacoes:
        for t in transacoes[:8]:
            icone = t.get("categoria_icone", "📌") or "📌"
            cat = t.get("categoria_nome", "Sem categoria") or "Sem categoria"
            transacao_row(t["data"], t["descricao"], cat, icone, t["valor"], t["tipo"])
    else:
        st.markdown("""
            <div style="text-align:center; padding:2rem; color:#9CA3AF;">
                <div style="font-size:2.5rem; margin-bottom:0.5rem;">🐷</div>
                <div>Nenhuma transacao neste periodo. Comece registrando!</div>
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# ABA - GASTOS
# =====================================================

def aba_gastos():
    usuario_id = st.session_state.usuario["id"]
    categorias = db.listar_categorias(usuario_id, tipo="gasto")
    cat_opcoes = {f"{c['icone']} {c['nome']}": c["id"] for c in categorias}

    section_header("➕", "Registrar Novo Gasto")
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

    section_header("📋", "Historico de Gastos")
    hoje = date.today()
    col_f1, col_f2, col_spacer = st.columns([1, 1, 2])
    with col_f1:
        mes_filtro = st.selectbox("Mes", range(1, 13), index=hoje.month - 1,
                                  format_func=lambda x: MESES[x - 1], key="gasto_mes")
    with col_f2:
        ano_filtro = st.number_input("Ano", min_value=2020, max_value=2030,
                                     value=hoje.year, key="gasto_ano")

    gastos = db.listar_transacoes(usuario_id, tipo="gasto", mes=mes_filtro, ano=ano_filtro)

    if gastos:
        total = sum(g["valor"] for g in gastos)
        st.markdown(f"""
            <div class="metric-card gasto" style="margin-bottom: 1.5rem;">
                <div class="metric-label">Total de Gastos no Periodo</div>
                <div class="metric-value">R$ {total:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

        for g in gastos:
            icone = g.get("categoria_icone", "📌") or "📌"
            cat = g.get("categoria_nome", "Sem categoria") or "Sem categoria"
            transacao_row(g["data"], g["descricao"], cat, icone, g["valor"], "gasto")

        with st.expander("Excluir um gasto"):
            opcoes_del = {f"{g['data']} - {g['descricao']} (R$ {g['valor']:,.2f})": g["id"] for g in gastos}
            gasto_del = st.selectbox("Selecione o gasto", list(opcoes_del.keys()), key="del_gasto")
            if st.button("Excluir", key="btn_del_gasto", type="secondary"):
                db.deletar_transacao(opcoes_del[gasto_del], usuario_id)
                st.success("Gasto excluido!")
                st.rerun()
    else:
        st.markdown("""
            <div style="text-align:center; padding:3rem; color:#9CA3AF;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">💸</div>
                <div>Nenhum gasto registrado neste periodo</div>
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# ABA - RECEITAS
# =====================================================

def aba_receitas():
    usuario_id = st.session_state.usuario["id"]
    categorias = db.listar_categorias(usuario_id, tipo="receita")
    cat_opcoes = {f"{c['icone']} {c['nome']}": c["id"] for c in categorias}

    section_header("➕", "Registrar Nova Receita")
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

    section_header("📋", "Historico de Receitas")
    hoje = date.today()
    col_f1, col_f2, col_spacer = st.columns([1, 1, 2])
    with col_f1:
        mes_filtro = st.selectbox("Mes", range(1, 13), index=hoje.month - 1,
                                  format_func=lambda x: MESES[x - 1], key="receita_mes")
    with col_f2:
        ano_filtro = st.number_input("Ano", min_value=2020, max_value=2030,
                                     value=hoje.year, key="receita_ano")

    receitas = db.listar_transacoes(usuario_id, tipo="receita", mes=mes_filtro, ano=ano_filtro)

    if receitas:
        total = sum(r["valor"] for r in receitas)
        st.markdown(f"""
            <div class="metric-card receita" style="margin-bottom: 1.5rem;">
                <div class="metric-label">Total de Receitas no Periodo</div>
                <div class="metric-value">R$ {total:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

        for r in receitas:
            icone = r.get("categoria_icone", "📌") or "📌"
            cat = r.get("categoria_nome", "Sem categoria") or "Sem categoria"
            transacao_row(r["data"], r["descricao"], cat, icone, r["valor"], "receita")

        with st.expander("Excluir uma receita"):
            opcoes_del = {f"{r['data']} - {r['descricao']} (R$ {r['valor']:,.2f})": r["id"] for r in receitas}
            rec_del = st.selectbox("Selecione a receita", list(opcoes_del.keys()), key="del_receita")
            if st.button("Excluir", key="btn_del_receita", type="secondary"):
                db.deletar_transacao(opcoes_del[rec_del], usuario_id)
                st.success("Receita excluida!")
                st.rerun()
    else:
        st.markdown("""
            <div style="text-align:center; padding:3rem; color:#9CA3AF;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">💰</div>
                <div>Nenhuma receita registrada neste periodo</div>
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# ABA - INVESTIMENTOS
# =====================================================

def aba_investimentos():
    usuario_id = st.session_state.usuario["id"]
    tipos_invest = ["Renda Fixa", "Acoes", "FIIs", "Tesouro Direto", "CDB",
                    "Poupanca", "Cripto", "Outros"]

    section_header("➕", "Registrar Novo Investimento")
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

    section_header("💼", "Meus Investimentos")
    investimentos = db.listar_investimentos(usuario_id)

    if investimentos:
        total_investido = sum(i["valor_investido"] for i in investimentos)
        total_atual = sum(i["valor_atual"] for i in investimentos)
        rendimento = total_atual - total_investido
        pct = (rendimento / total_investido * 100) if total_investido > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card("Total Investido", f"R$ {total_investido:,.2f}", "saldo")
        with col2:
            metric_card("Valor Atual", f"R$ {total_atual:,.2f}",
                        "receita" if rendimento >= 0 else "gasto")
        with col3:
            metric_card_delta("Rendimento", f"R$ {rendimento:,.2f}",
                              f"{pct:+.2f}%",
                              "receita" if rendimento >= 0 else "gasto")

        st.markdown("<br>", unsafe_allow_html=True)

        # Grafico donut por tipo
        df_inv = pd.DataFrame(investimentos)
        df_tipo = df_inv.groupby("tipo")["valor_atual"].sum().reset_index()
        fig = px.pie(df_tipo, values="valor_atual", names="tipo", hole=0.55,
                     color_discrete_sequence=[
                         "#6C5CE7", "#FF6B8A", "#00D2D3", "#FDCB6E",
                         "#00B894", "#E17055", "#A29BFE", "#74B9FF"
                     ])
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig, use_container_width=True)

        for inv in investimentos:
            rend = inv["valor_atual"] - inv["valor_investido"]
            rend_pct = (rend / inv["valor_investido"] * 100) if inv["valor_investido"] > 0 else 0
            badge_class = "up" if rend >= 0 else "down"
            emoji = "📈" if rend >= 0 else "📉"

            with st.expander(f"{emoji} {inv['nome']} ({inv['tipo']}) — R$ {inv['valor_atual']:,.2f}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Investido:** R$ {inv['valor_investido']:,.2f}")
                with col2:
                    st.write(f"**Atual:** R$ {inv['valor_atual']:,.2f}")
                with col3:
                    st.markdown(
                        f"**Rendimento:** <span class='invest-badge {badge_class}'>"
                        f"R$ {rend:,.2f} ({rend_pct:+.2f}%)</span>",
                        unsafe_allow_html=True
                    )

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
                    if st.button("Excluir Investimento", key=f"btn_del_inv_{inv['id']}", type="secondary"):
                        db.deletar_investimento(inv["id"], usuario_id)
                        st.success("Investimento excluido!")
                        st.rerun()
    else:
        st.markdown("""
            <div style="text-align:center; padding:3rem; color:#9CA3AF;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">📈</div>
                <div>Nenhum investimento registrado. Comece a investir!</div>
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# ABA - METAS
# =====================================================

def aba_metas():
    usuario_id = st.session_state.usuario["id"]

    section_header("➕", "Criar Nova Meta")
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

    section_header("🎯", "Minhas Metas")
    metas = db.listar_metas(usuario_id)

    if metas:
        for meta in metas:
            progresso = (meta["valor_atual"] / meta["valor_alvo"]) if meta["valor_alvo"] > 0 else 0
            progresso = min(progresso, 1.0)
            emoji = "🎯" if progresso < 1.0 else "🏆"
            pct_display = f"{progresso:.0%}"

            with st.expander(
                f"{emoji} {meta['nome']} — {pct_display} concluida "
                f"(R$ {meta['valor_atual']:,.2f} / R$ {meta['valor_alvo']:,.2f})"
            ):
                st.progress(progresso)

                falta = meta["valor_alvo"] - meta["valor_atual"]
                if falta > 0:
                    st.markdown(f"""
                        <div style="text-align:center; padding:0.5rem; color:#6B7280; font-size:0.95rem;">
                            Faltam <strong style="color:#FF6B8A;">R$ {falta:,.2f}</strong> para alcancar a meta
                        </div>
                    """, unsafe_allow_html=True)
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
                    if st.button("Excluir Meta", key=f"btn_del_meta_{meta['id']}", type="secondary"):
                        db.deletar_meta(meta["id"], usuario_id)
                        st.success("Meta excluida!")
                        st.rerun()
    else:
        st.markdown("""
            <div style="text-align:center; padding:3rem; color:#9CA3AF;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">🎯</div>
                <div>Nenhuma meta criada ainda. Defina seus objetivos!</div>
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# APP PRINCIPAL
# =====================================================

def app_principal():
    usuario_id = st.session_state.usuario["id"]

    # Sidebar moderna
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-brand">
                {get_logo_sidebar_html(90)}
                <div class="sidebar-brand-name">Porquinho</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="sidebar-user">
                Ola, <strong>{st.session_state.usuario['nome']}</strong>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Resumo rapido na sidebar
        hoje = date.today()
        resumo = db.resumo_mensal(usuario_id, hoje.month, hoje.year)
        st.markdown(f"""
            <div class="nav-info">
                <div class="nav-info-label">Saldo Atual</div>
                <div class="nav-info-value">R$ {resumo['saldo']:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="nav-info">
                <div class="nav-info-label">Investimentos</div>
                <div class="nav-info-value">
                    R$ {sum(i['valor_atual'] for i in db.listar_investimentos(usuario_id)):,.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        if st.button("Sair da conta", use_container_width=True):
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
