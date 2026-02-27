import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Clientes | Evolution Nutrition",
    page_icon="💚",
    layout="wide"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
        .metric-card {
            background: linear-gradient(135deg, #1a1f2e, #232938);
            border: 1px solid #2a3045;
            border-radius: 16px;
            padding: 24px;
            text-align: center;
        }
        .metric-value { font-size: 2.2rem; font-weight: 700; color: #4ade80; }
        .metric-label { font-size: 0.85rem; color: #8892a4; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }
        h1 { color: #f1f5f9 !important; }
        h2, h3 { color: #cbd5e1 !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# TELA DE LOGIN
# ============================================================

def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 💚 Evolution Nutrition Lab")
        st.markdown("#### Dashboard de Clientes — Acesso Restrito")
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
# CARREGAMENTO DO CSV VIA GOOGLE DRIVE
# ============================================================

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
# DASHBOARD PRINCIPAL
# ============================================================

def mostrar_dashboard():
    df = carregar_dados()

    col_logout = st.columns([8, 1])[1]
    with col_logout:
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()

    st.markdown("## 💚 Dashboard de Clientes")
    st.markdown(f"**Evolution Nutrition Lab** — Olá, `{st.session_state.usuario_logado}`!")
    st.divider()

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

    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.markdown("### 🛒 Nível de Compra")
        ordem = ["1ª Compra", "2ª Compra", "3ª Compra", "4ª Compra", "5ª Compra +"]
        contagem = df["classificacao"].value_counts().reindex(ordem).reset_index()
        contagem.columns = ["classificacao", "total"]
        contagem["cor"] = range(len(contagem))
        fig = px.bar(contagem, x="classificacao", y="total",
                     color="cor",
                     color_continuous_scale=["#4ade80", "#22d3ee", "#818cf8", "#f472b6", "#fb923c"],
                     text="total")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside", textfont_color="#cbd5e1")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#cbd5e1", family="Sora"),
                          coloraxis_showscale=False,
                          xaxis=dict(gridcolor="#2a3045"),
                          yaxis=dict(gridcolor="#2a3045"),
                          margin=dict(t=40, b=20),
                          xaxis_title="", yaxis_title="Clientes")
        st.plotly_chart(fig, use_container_width=True)

    with col_dir:
        st.markdown("### 🗺️ Clientes por Estado")
        estados = df["estado"].dropna()
        estados = estados[estados.str.strip() != ""]
        top = estados.value_counts().head(15).reset_index()
        top.columns = ["estado", "total"]
        fig = px.bar(top, x="total", y="estado", orientation="h",
                     color="total", color_continuous_scale=["#1a3a2a","#4ade80"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#cbd5e1", family="Sora"), coloraxis_showscale=False,
                          yaxis=dict(categoryorder="total ascending"), margin=dict(t=20, b=20),
                          xaxis=dict(gridcolor="#2a3045"), yaxis_title="", xaxis_title="Clientes")
        st.plotly_chart(fig, use_container_width=True)

    col_esq2, col_dir2 = st.columns(2)

    with col_esq2:
        st.markdown("### 📈 Novos Clientes por Mês")
        df_mes = df.dropna(subset=["atualizado_em"]).copy()
        df_mes["mes"] = df_mes["atualizado_em"].dt.to_period("M").astype(str)
        evolucao = df_mes.groupby("mes").size().reset_index(name="total").tail(24)
        fig = px.line(evolucao, x="mes", y="total", markers=True, line_shape="spline")
        fig.update_traces(line_color="#4ade80", marker=dict(color="#4ade80", size=6),
                          fill="tozeroy", fillcolor="rgba(74,222,128,0.1)")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#cbd5e1", family="Sora"),
                          xaxis=dict(gridcolor="#2a3045", tickangle=-45),
                          yaxis=dict(gridcolor="#2a3045"), margin=dict(t=20, b=60),
                          xaxis_title="", yaxis_title="Clientes")
        st.plotly_chart(fig, use_container_width=True)

    with col_dir2:
        st.markdown("### 🏙️ Top 15 Cidades")
        cidades = df["cidade"].dropna()
        cidades = cidades[cidades.str.strip() != ""]
        top = cidades.value_counts().head(15).reset_index()
        top.columns = ["cidade", "total"]
        fig = px.bar(top, x="total", y="cidade", orientation="h",
                     color="total", color_continuous_scale=["#1a2a3a","#22d3ee"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#cbd5e1", family="Sora"), coloraxis_showscale=False,
                          yaxis=dict(categoryorder="total ascending"), margin=dict(t=20, b=20),
                          xaxis=dict(gridcolor="#2a3045"), yaxis_title="", xaxis_title="Clientes")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("<p style='text-align:center; color:#4a5568; font-size:0.8rem;'>Evolution Nutrition Lab · Dashboard de Clientes · Dados via API Olist</p>",
                unsafe_allow_html=True)

# ============================================================
# EXECUÇÃO
# ============================================================

if verificar_login():
    mostrar_dashboard()
