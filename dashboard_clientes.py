import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests
from PIL import Image

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Clientes | Evolution Nutrition",
    page_icon="👑",
    layout="wide"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Sora', sans-serif; background-color: #f8f4ff; }
        .main { background-color: #f8f4ff; }

        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 20px 24px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(200,80,180,0.10);
            border-left: 4px solid #d63aad;
        }
        .metric-value { font-size: 2rem; font-weight: 700; background: linear-gradient(90deg, #d63aad, #7c5cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .metric-label { font-size: 0.78rem; color: #999; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }

        .login-card {
            background: white;
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 8px 40px rgba(200,80,180,0.15);
        }

        h1, h2, h3 { color: #3d2e6b !important; }
        .stButton > button {
            background: linear-gradient(90deg, #d63aad, #7c5cbf);
            color: white;
            border: none;
            border-radius: 8px;
            font-family: 'Sora', sans-serif;
            font-weight: 600;
        }
        .stButton > button:hover { opacity: 0.9; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def carregar_imagem_drive(url):
    file_id = url.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resposta = requests.get(download_url)
    return Image.open(io.BytesIO(resposta.content))

@st.cache_data(ttl=3600)
def carregar_dados():
    url = st.secrets["GOOGLE_DRIVE_URL"]
    file_id = url.split("/d/")[1].split("/")[0]
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resposta = requests.get(download_url)
    resposta.raise_for_status()
    df = pd.read_csv(io.StringIO(resposta.text), encoding="utf-8-sig")
    df["atualizado_em"] = pd.to_datetime(df["atualizado_em"], format="%d/%m/%Y %H:%M", errors="coerce")
    df["ultimo_pedido_confirmado"] = pd.to_datetime(df["ultimo_pedido_confirmado"], format="%d/%m/%Y %H:%M", errors="coerce")
    return df

# ============================================================
# PALETA DE CORES
# ============================================================

LOGO_URL = "https://drive.google.com/file/d/1yZLs4Z8FnnxRldzaGBgOCRyQTl9m-Xy2/view?usp=sharing"

CORES_NIVEL = {
    "1ª Compra":   "#d63aad",
    "2ª Compra":   "#a855b5",
    "3ª Compra":   "#7c5cbf",
    "4ª Compra":   "#5b6fcf",
    "5ª Compra +": "#3b82d4",
}
GRADIENTE = ["#d63aad", "#a855b5", "#7c5cbf", "#5b6fcf", "#3b82d4"]

# ============================================================
# TELA DE LOGIN
# ============================================================

def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        return True

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo centralizado
        try:
            logo = carregar_imagem_drive(LOGO_URL)
            st.image(logo, width=200)
        except:
            st.markdown("## 👑 Evolution Nutrition Lab")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#7c5cbf; text-align:center'>Dashboard de Clientes — Acesso Restrito</h4>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        usuario = st.text_input("Usuário")
        senha   = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):
            usuarios = st.secrets.get("usuarios", {})
            if usuario in usuarios and usuarios[usuario] == senha:
                st.session_state.autenticado = True
                st.session_state.usuario_logado = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    return False

# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================

def mostrar_dashboard():
    df_completo = carregar_dados()

    # --- Header com logo ---
    col_logo, col_titulo, col_logout = st.columns([1, 7, 1])
    with col_logo:
        try:
            logo = carregar_imagem_drive(LOGO_URL)
            st.image(logo, width=80)
        except:
            st.markdown("👑")
    with col_titulo:
        st.markdown("<h2 style='color:#3d2e6b; margin-bottom:0'>Dashboard de Clientes</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#999; margin-top:0'>Evolution Nutrition Lab — Olá, <b style='color:#d63aad'>{st.session_state.usuario_logado}</b>!</p>", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()

    st.divider()

    # --- Filtro de Nível de Compra ---
    ordem = ["Todos", "1ª Compra", "2ª Compra", "3ª Compra", "4ª Compra", "5ª Compra +"]

    if "nivel_selecionado" not in st.session_state:
        st.session_state.nivel_selecionado = "Todos"

    st.markdown("#### 🎯 Filtrar por Nível de Compra")
    cols_filtro = st.columns(len(ordem))
    for i, nivel_btn in enumerate(ordem):
        with cols_filtro[i]:
            ativo = st.session_state.nivel_selecionado == nivel_btn
            if st.button(nivel_btn, key=f"btn_{nivel_btn}", use_container_width=True):
                st.session_state.nivel_selecionado = nivel_btn
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Aplica filtro ---
    nivel = st.session_state.nivel_selecionado
    df = df_completo if nivel == "Todos" else df_completo[df_completo["classificacao"] == nivel]

    # --- Métricas ---
    total       = len(df)
    compraram   = df[df["pedidos_confirmados"] > 0]
    recorrentes = df[df["pedidos_confirmados"] >= 2]
    cancelados  = df[(df["pedidos_confirmados"] == 0) & (df["pedidos_cancelados"] > 0)]

    col1, col2, col3, col4 = st.columns(4)
    for col, valor, label in [
        (col1, total, "Total de Clientes"),
        (col2, len(compraram), "Compraram ao menos 1x"),
        (col3, len(recorrentes), "Clientes Recorrentes"),
        (col4, len(cancelados), "Só Cancelamentos"),
    ]:
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{valor:,}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Linha 1: Nível de Compra + Estados ---
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.markdown("### 🛒 Nível de Compra")
        contagem = df_completo["classificacao"].value_counts().reindex(ordem[1:]).reset_index()
        contagem.columns = ["classificacao", "total"]

        fig = px.bar(contagem, x="classificacao", y="total",
                     color="classificacao",
                     color_discrete_map=CORES_NIVEL,
                     text="total")

        if nivel != "Todos":
            for trace in fig.data:
                trace.opacity = 1.0 if trace.name == nivel else 0.25

        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="#3d2e6b", family="Sora"),
            showlegend=False,
            xaxis=dict(gridcolor="#f0eafa"),
            yaxis=dict(gridcolor="#f0eafa"),
            margin=dict(t=40, b=20),
            xaxis_title="", yaxis_title="Clientes"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_dir:
        st.markdown("### 🗺️ Clientes por Estado")
        estados = df["estado"].dropna()
        estados = estados[estados.str.strip() != ""]
        top = estados.value_counts().head(15).reset_index()
        top.columns = ["estado", "total"]
        fig = px.bar(top, x="total", y="estado", orientation="h",
                     color="total", color_continuous_scale=GRADIENTE)
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="#3d2e6b", family="Sora"),
            coloraxis_showscale=False,
            yaxis=dict(categoryorder="total ascending", gridcolor="#f0eafa"),
            xaxis=dict(gridcolor="#f0eafa"),
            margin=dict(t=20, b=20),
            yaxis_title="", xaxis_title="Clientes"
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Linha 2: Evolução + Cidades ---
    col_esq2, col_dir2 = st.columns(2)

    with col_esq2:
        st.markdown("### 📈 Novos Clientes por Mês")
        df_mes = df.dropna(subset=["atualizado_em"]).copy()
        df_mes["mes"] = df_mes["atualizado_em"].dt.to_period("M").astype(str)
        evolucao = df_mes.groupby("mes").size().reset_index(name="total").tail(24)
        fig = px.line(evolucao, x="mes", y="total", markers=True, line_shape="spline")
        fig.update_traces(line_color="#d63aad", marker=dict(color="#d63aad", size=6),
                          fill="tozeroy", fillcolor="rgba(214,58,173,0.08)")
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="#3d2e6b", family="Sora"),
            xaxis=dict(gridcolor="#f0eafa", tickangle=-45),
            yaxis=dict(gridcolor="#f0eafa"),
            margin=dict(t=20, b=60),
            xaxis_title="", yaxis_title="Clientes"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_dir2:
        st.markdown("### 🏙️ Top 15 Cidades")
        cidades = df["cidade"].dropna()
        cidades = cidades[cidades.str.strip() != ""]
        top = cidades.value_counts().head(15).reset_index()
        top.columns = ["cidade", "total"]
        fig = px.bar(top, x="total", y="cidade", orientation="h",
                     color="total", color_continuous_scale=GRADIENTE)
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="#3d2e6b", family="Sora"),
            coloraxis_showscale=False,
            yaxis=dict(categoryorder="total ascending", gridcolor="#f0eafa"),
            xaxis=dict(gridcolor="#f0eafa"),
            margin=dict(t=20, b=20),
            yaxis_title="", xaxis_title="Clientes"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("<p style='text-align:center; color:#ccc; font-size:0.8rem;'>Evolution Nutrition Lab · Dashboard de Clientes · Dados via API Olist</p>",
                unsafe_allow_html=True)

# ============================================================
# EXECUÇÃO
# ============================================================

if verificar_login():
    mostrar_dashboard()

# ============================================================

if verificar_login():
    mostrar_dashboard()
