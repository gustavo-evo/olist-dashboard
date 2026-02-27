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
        .block-container { padding-top: 2rem; }

        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 22px 24px;
            text-align: center;
            box-shadow: 0 2px 16px rgba(214,58,173,0.08);
            border-top: 4px solid transparent;
            border-image: linear-gradient(90deg, #d63aad, #7c5cbf) 1;
            border-image-slice: 1;
            border-radius: 16px;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #d63aad, #7c5cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-label {
            font-size: 0.75rem;
            color: #aaa;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }

        /* Filtro pills */
        .filtro-container {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .pill {
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            border: 2px solid #d63aad;
            color: #d63aad;
            background: white;
            transition: all 0.2s;
        }
        .pill.ativo {
            background: linear-gradient(90deg, #d63aad, #7c5cbf);
            color: white;
            border-color: transparent;
        }

        /* Seção título */
        .section-title {
            font-size: 1rem;
            font-weight: 700;
            color: #3d2e6b;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        h1, h2, h3 { color: #3d2e6b !important; }

        /* Botão sair */
        .stButton > button {
            background: linear-gradient(90deg, #d63aad, #7c5cbf) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 6px 20px !important;
            font-family: 'Sora', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }

        /* Radio como pills */
        div[data-testid="stHorizontalBlock"] .stRadio > div {
            flex-direction: row;
            gap: 8px;
        }
        div[data-testid="stHorizontalBlock"] .stRadio > div > label {
            background: white;
            border: 2px solid #d63aad;
            border-radius: 50px;
            padding: 6px 18px;
            color: #d63aad;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
        }
        div[data-testid="stHorizontalBlock"] .stRadio > div > label[data-checked="true"] {
            background: linear-gradient(90deg, #d63aad, #7c5cbf);
            color: white;
            border-color: transparent;
        }

        /* Login */
        .login-wrapper {
            background: white;
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 8px 40px rgba(214,58,173,0.12);
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

LOGO_URL = "https://drive.google.com/file/d/1yZLs4Z8FnnxRldzaGBgOCRyQTl9m-Xy2/view?usp=sharing"

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

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            logo = carregar_imagem_drive(LOGO_URL)
            c1, c2, c3 = st.columns([1,2,1])
            with c2:
                st.image(logo, use_container_width=True)
        except:
            st.markdown("<h2 style='text-align:center;color:#3d2e6b'>👑 Evolution Nutrition Lab</h2>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#7c5cbf; text-align:center'>Dashboard de Clientes — Acesso Restrito</h4>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha   = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Entrar →", use_container_width=True):
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

    # Header
    col_logo, col_titulo, col_logout = st.columns([1, 8, 1])
    with col_logo:
        try:
            logo = carregar_imagem_drive(LOGO_URL)
            st.image(logo, width=90)
        except:
            st.markdown("👑")
    with col_titulo:
        st.markdown("<h2 style='color:#3d2e6b; margin-bottom:0; padding-top:10px'>Dashboard de Clientes</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#bbb; margin-top:2px; font-size:0.9rem'>Evolution Nutrition Lab — Olá, <b style='color:#d63aad'>{st.session_state.get('usuario_logado', '')}</b>!</p>", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sair →"):
            st.session_state.autenticado = False
            st.rerun()

    st.divider()

    # Filtro com radio estilizado como pills
    ordem = ["Todos", "1ª Compra", "2ª Compra", "3ª Compra", "4ª Compra", "5ª Compra +"]

    nivel = st.radio(
        "🎯 **Filtrar por Nível de Compra**",
        options=ordem,
        horizontal=True,
        key="nivel_radio"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Aplica filtro
    df = df_completo if nivel == "Todos" else df_completo[df_completo["classificacao"] == nivel]

    # Métricas
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

    # Linha 1
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.markdown("### 🛒 Nível de Compra")
        contagem = df_completo["classificacao"].value_counts().reindex(ordem[1:]).reset_index()
        contagem.columns = ["classificacao", "total"]
        fig = px.bar(contagem, x="classificacao", y="total",
                     color="classificacao",
                     color_discrete_map=CORES_NIVEL,
                     text="total",
                     custom_data=["classificacao"])
        if nivel != "Todos":
            for trace in fig.data:
                trace.opacity = 1.0 if trace.name == nivel else 0.2
        fig.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Clientes: %{y:,}<extra></extra>"
        )
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="#3d2e6b", family="Sora"),
            showlegend=False,
            xaxis=dict(gridcolor="#f5f0ff", showgrid=False),
            yaxis=dict(gridcolor="#f5f0ff"),
            margin=dict(t=40, b=10),
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
                     color="total", color_continuous_scale=GRADIENTE,
                     text="total")
        fig.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Clientes: %{x:,}<extra></extra>"
        )
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="#3d2e6b", family="Sora"),
            coloraxis_showscale=False,
            yaxis=dict(categoryorder="total ascending", gridcolor="#f5f0ff"),
            xaxis=dict(gridcolor="#f5f0ff", showgrid=False),
            margin=dict(t=10, b=10, r=60),
            yaxis_title="", xaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    # Linha 2
    col_esq2, col_dir2 = st.columns(2)

    with col_esq2:
        st.markdown("### 📈 Novos Clientes por Mês")
        df_mes = df.dropna(subset=["atualizado_em"]).copy()
        df_mes["mes"] = df_mes["atualizado_em"].dt.to_period("M").astype(str)
        evolucao = df_mes.groupby("mes").size().reset_index(name="total").tail(24)
        fig = px.line(evolucao, x="mes", y="total", markers=True, line_shape="spline")
        fig.update_traces(
            line_color="#d63aad",
            marker=dict(color="#7c5cbf", size=7, line=dict(color="white", width=2)),
            fill="tozeroy",
            fillcolor="rgba(214,58,173,0.06)",
            hovertemplate="<b>%{x}</b><br>Clientes: %{y:,}<extra></extra>"
        )
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="#3d2e6b", family="Sora"),
            xaxis=dict(gridcolor="#f5f0ff", tickangle=-45, showgrid=False),
            yaxis=dict(gridcolor="#f5f0ff"),
            margin=dict(t=10, b=60),
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
                     color="total", color_continuous_scale=GRADIENTE,
                     text="total")
        fig.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Clientes: %{x:,}<extra></extra>"
        )
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="#3d2e6b", family="Sora"),
            coloraxis_showscale=False,
            yaxis=dict(categoryorder="total ascending", gridcolor="#f5f0ff"),
            xaxis=dict(gridcolor="#f5f0ff", showgrid=False),
            margin=dict(t=10, b=10, r=60),
            yaxis_title="", xaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("<p style='text-align:center; color:#ddd; font-size:0.78rem'>Evolution Nutrition Lab · Dashboard de Clientes · Dados via API Olist</p>",
                unsafe_allow_html=True)

# ============================================================
# EXECUÇÃO
# ============================================================

if verificar_login():
    mostrar_dashboard()
