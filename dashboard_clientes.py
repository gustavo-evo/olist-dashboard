import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests
from PIL import Image

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
            border-top: 4px solid #d63aad;
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
        h1, h2, h3 { color: #3d2e6b !important; }
        .stButton > button {
            background: linear-gradient(90deg, #d63aad, #7c5cbf) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            font-family: 'Sora', sans-serif !important;
            font-weight: 600 !important;
        }
    </style>
""", unsafe_allow_html=True)

LOGO_URL = "https://drive.google.com/file/d/1yZLs4Z8FnnxRldzaGBgOCRyQTl9m-Xy2/view?usp=sharing"
CORES_NIVEL = {
    "1ª Compra":   "#d63aad",
    "2ª Compra":   "#a855b5",
    "3ª Compra":   "#7c5cbf",
    "4ª Compra":   "#5b6fcf",
    "5ª Compra +": "#3b82d4",
}
GRADIENTE = ["#d63aad", "#a855b5", "#7c5cbf", "#5b6fcf", "#3b82d4"]

ORDEM_FAIXAS = ["Menor de 20", "20 – 29", "30 – 39", "40 – 49", "50 – 59", "60+"]
CORES_FAIXAS = {
    "Menor de 20": "#f9a8d4",
    "20 – 29":     "#d63aad",
    "30 – 39":     "#a855b5",
    "40 – 49":     "#7c5cbf",
    "50 – 59":     "#5b6fcf",
    "60+":         "#3b82d4",
}

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def faixa_etaria(idade):
    if pd.isna(idade):   return None
    elif idade < 20:     return "Menor de 20"
    elif idade < 30:     return "20 – 29"
    elif idade < 40:     return "30 – 39"
    elif idade < 50:     return "40 – 49"
    elif idade < 60:     return "50 – 59"
    else:                return "60+"

def carregar_imagem_drive(url):
    file_id = url.split("/d/")[1].split("/")[0]
    r = requests.get(f"https://drive.google.com/uc?export=download&id={file_id}")
    return Image.open(io.BytesIO(r.content))

@st.cache_data(ttl=0)
def carregar_dados():
    url = st.secrets["GOOGLE_DRIVE_URL"]
    file_id = url.split("/d/")[1].split("/")[0]
    r = requests.get(f"https://drive.google.com/uc?export=download&id={file_id}")
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), encoding="utf-8-sig")
    df["atualizado_em"] = pd.to_datetime(df["atualizado_em"], format="%d/%m/%Y %H:%M", errors="coerce")
    df["ultimo_pedido_confirmado"] = pd.to_datetime(df["ultimo_pedido_confirmado"], format="%d/%m/%Y %H:%M", errors="coerce")
    return df

# ============================================================
# LOGIN
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
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(logo, width=200)
        except:
            st.markdown("<h2 style='text-align:center;color:#3d2e6b'>👑</h2>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#7c5cbf; text-align:center'>Dashboard de Clientes — Acesso Restrito</h4>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        usuario = st.text_input("Usuário", placeholder="Digite seu usuário", key="login_usuario")
        senha   = st.text_input("Senha", type="password", placeholder="Digite sua senha", key="login_senha")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Entrar →", use_container_width=True, key="btn_entrar"):
            usuarios = st.secrets.get("usuarios", {})
            if usuario in usuarios and usuarios[usuario] == senha:
                st.session_state.autenticado = True
                st.session_state.usuario_logado = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    return False

# ============================================================
# DASHBOARD
# ============================================================

def mostrar_dashboard():
    df_completo = carregar_dados()

    # DEBUG - remover depois
    st.caption(f"📦 CSV carregado: {len(df_completo):,} linhas | Colunas: {list(df_completo.columns[:5])} | Classificações: {df_completo['classificacao'].unique().tolist()}")

    col_logo, col_titulo, col_logout = st.columns([1, 8, 1])
    with col_logo:
        try:
            logo = carregar_imagem_drive(LOGO_URL)
            st.image(logo, width=90)
        except:
            st.markdown("👑")
    with col_titulo:
        st.markdown("<h2 style='color:#3d2e6b; margin-bottom:0; padding-top:10px'>Dashboard de Clientes</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#bbb; margin-top:2px; font-size:0.9rem'>Evolution Nutrition Lab — Olá, <b style='color:#d63aad'>{st.session_state.get('usuario_logado','')}</b>!</p>", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sair →", key="btn_sair"):
            st.session_state.autenticado = False
            st.rerun()

    st.divider()

    ordem = ["Todos", "1ª Compra", "2ª Compra", "3ª Compra", "4ª Compra", "5ª Compra +"]
    nivel = st.radio("🎯 **Filtrar por Nível de Compra**", options=ordem, horizontal=True, key="nivel_radio")

    st.markdown("<br>", unsafe_allow_html=True)

    df = df_completo if nivel == "Todos" else df_completo[df_completo["classificacao"] == nivel]

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

    # ----------------------------------------------------------
    # GRÁFICOS PRINCIPAIS
    # ----------------------------------------------------------

    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.markdown("### 🛒 Nível de Compra")
        contagem = df_completo["classificacao"].value_counts().reindex(ordem[1:]).reset_index()
        contagem.columns = ["classificacao", "total"]
        fig = px.bar(contagem, x="classificacao", y="total",
                     color="classificacao", color_discrete_map=CORES_NIVEL, text="total")
        if nivel != "Todos":
            for trace in fig.data:
                trace.opacity = 1.0 if trace.name == nivel else 0.2
        fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                          hovertemplate="<b>%{x}</b><br>Clientes: %{y:,}<extra></extra>")
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font=dict(color="#3d2e6b", family="Sora"), showlegend=False,
                          xaxis=dict(gridcolor="#f5f0ff", showgrid=False),
                          yaxis=dict(gridcolor="#f5f0ff"),
                          margin=dict(t=40, b=10), xaxis_title="", yaxis_title="Clientes")
        st.plotly_chart(fig, key="chart_nivel")

    with col_dir:
        st.markdown("### 🗺️ Clientes por Estado")
        estados = df["estado"].dropna()
        estados = estados[estados.str.strip() != ""]
        top = estados.value_counts().head(15).reset_index()
        top.columns = ["estado", "total"]
        fig = px.bar(top, x="total", y="estado", orientation="h",
                     color="total", color_continuous_scale=GRADIENTE, text="total")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                          hovertemplate="<b>%{y}</b><br>Clientes: %{x:,}<extra></extra>")
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font=dict(color="#3d2e6b", family="Sora"), coloraxis_showscale=False,
                          yaxis=dict(categoryorder="total ascending", gridcolor="#f5f0ff"),
                          xaxis=dict(gridcolor="#f5f0ff", showgrid=False),
                          margin=dict(t=10, b=10, r=60), yaxis_title="", xaxis_title="")
        st.plotly_chart(fig, key="chart_estados")

    col_esq2, col_dir2 = st.columns(2)

    with col_esq2:
        st.markdown("### 📈 Novos Clientes por Mês")
        df_mes = df.dropna(subset=["atualizado_em"]).copy()
        df_mes["mes"] = df_mes["atualizado_em"].dt.to_period("M").astype(str)
        evolucao = df_mes.groupby("mes").size().reset_index(name="total").tail(24)
        fig = px.line(evolucao, x="mes", y="total", markers=True, line_shape="spline")
        fig.update_traces(line_color="#d63aad",
                          marker=dict(color="#7c5cbf", size=7, line=dict(color="white", width=2)),
                          fill="tozeroy", fillcolor="rgba(214,58,173,0.06)",
                          hovertemplate="<b>%{x}</b><br>Clientes: %{y:,}<extra></extra>")
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font=dict(color="#3d2e6b", family="Sora"),
                          xaxis=dict(gridcolor="#f5f0ff", tickangle=-45, showgrid=False),
                          yaxis=dict(gridcolor="#f5f0ff"),
                          margin=dict(t=10, b=60), xaxis_title="", yaxis_title="Clientes")
        st.plotly_chart(fig, key="chart_evolucao")

    with col_dir2:
        st.markdown("### 🏙️ Top 15 Cidades")
        cidades = df["cidade"].dropna()
        cidades = cidades[cidades.str.strip() != ""]
        top = cidades.value_counts().head(15).reset_index()
        top.columns = ["cidade", "total"]
        fig = px.bar(top, x="total", y="cidade", orientation="h",
                     color="total", color_continuous_scale=GRADIENTE, text="total")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                          hovertemplate="<b>%{y}</b><br>Clientes: %{x:,}<extra></extra>")
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font=dict(color="#3d2e6b", family="Sora"), coloraxis_showscale=False,
                          yaxis=dict(categoryorder="total ascending", gridcolor="#f5f0ff"),
                          xaxis=dict(gridcolor="#f5f0ff", showgrid=False),
                          margin=dict(t=10, b=10, r=60), yaxis_title="", xaxis_title="")
        st.plotly_chart(fig, key="chart_cidades")

    # ----------------------------------------------------------
    # GÊNERO
    # ----------------------------------------------------------

    if "genero" in df.columns:
        st.divider()
        st.markdown("## 🚻 Distribuição por Gênero")
        st.markdown("<br>", unsafe_allow_html=True)

        col_g1, col_g2 = st.columns([1, 3])

        with col_g1:
            gen = df["genero"].value_counts()
            total_gen = gen.sum()
            for label, valor in gen.items():
                pct = valor / total_gen * 100
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:12px">
                        <div class="metric-value">{pct:.1f}%</div>
                        <div class="metric-label">{label}</div>
                    </div>
                """, unsafe_allow_html=True)

        with col_g2:
            gen_df = gen.reset_index()
            gen_df.columns = ["genero", "total"]
            fig = px.pie(gen_df, names="genero", values="total",
                         color="genero",
                         color_discrete_map={"Feminino": "#d63aad", "Masculino": "#5b6fcf"},
                         hole=0.55)
            fig.update_traces(texttemplate="%{label}<br><b>%{percent}</b>",
                              hovertemplate="<b>%{label}</b><br>Clientes: %{value:,}<extra></extra>")
            fig.update_layout(paper_bgcolor="white", font=dict(color="#3d2e6b", family="Sora"),
                              showlegend=False, margin=dict(t=10, b=10))
            st.plotly_chart(fig, key="chart_genero")

    # ----------------------------------------------------------
    # PÚBLICO-ALVO
    # ----------------------------------------------------------

    colunas_pub = {"data_nascimento", "genero", "classificacao"}
    if colunas_pub.issubset(df.columns):
        st.divider()
        st.markdown("## 🎯 Análise de Público-Alvo")
        st.markdown("<br>", unsafe_allow_html=True)

        df_pub = df.copy()
        df_pub["data_nascimento"] = pd.to_datetime(df_pub["data_nascimento"], format="%d/%m/%Y", errors="coerce")
        hoje = pd.Timestamp.now()
        df_pub["idade"] = ((hoje - df_pub["data_nascimento"]).dt.days / 365.25).fillna(-1).astype(int)
        df_pub["idade"] = df_pub["idade"].replace(-1, pd.NA)
        df_pub = df_pub[df_pub["idade"].between(14, 100)]
        df_pub["faixa"] = df_pub["idade"].apply(faixa_etaria)
        df_pub = df_pub[df_pub["faixa"].notna()]

        total_pub = len(df_pub)
        st.caption(f"Base com data de nascimento válida: **{total_pub:,} clientes** ({total_pub/len(df)*100:.1f}% do total filtrado)")
        st.markdown("<br>", unsafe_allow_html=True)

        # Gênero x Faixa etária
        st.markdown("### 👥 Gênero por Faixa Etária")
        gen_faixa = (
            df_pub.groupby(["faixa", "genero"])
            .size().reset_index(name="total")
        )
        gen_faixa["faixa"] = pd.Categorical(gen_faixa["faixa"], categories=ORDEM_FAIXAS, ordered=True)
        gen_faixa = gen_faixa.sort_values("faixa")

        fig = px.bar(gen_faixa, x="faixa", y="total", color="genero", barmode="group",
                     color_discrete_map={"Feminino": "#d63aad", "Masculino": "#5b6fcf"}, text="total")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                          hovertemplate="<b>%{x}</b> · %{fullData.name}<br>Clientes: %{y:,}<extra></extra>")
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font=dict(color="#3d2e6b", family="Sora"),
                          legend=dict(title="", orientation="h", y=1.08),
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f5f0ff"),
                          margin=dict(t=40, b=10), xaxis_title="", yaxis_title="Clientes")
        st.plotly_chart(fig, use_container_width=True, key="chart_gen_faixa")

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### 🏆 Top Faixas que Mais Compram")
            df_pub["pedidos_confirmados"] = pd.to_numeric(df_pub["pedidos_confirmados"], errors="coerce").fillna(0)
            media_compras = (
                df_pub.groupby("faixa")["pedidos_confirmados"]
                .agg(["mean", "count"])
                .rename(columns={"mean": "media", "count": "clientes"})
                .reindex(ORDEM_FAIXAS).dropna().reset_index()
            )
            media_compras["media"] = media_compras["media"].round(2)

            fig = px.bar(media_compras, x="faixa", y="media",
                         color="media", color_continuous_scale=GRADIENTE, text="media")
            fig.update_traces(
                texttemplate="%{text:.2f}", textposition="outside",
                hovertemplate="<b>%{x}</b><br>Média de compras: %{y:.2f}<br>Clientes: %{customdata[0]:,}<extra></extra>",
                customdata=media_compras[["clientes"]].values,
            )
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                              font=dict(color="#3d2e6b", family="Sora"),
                              coloraxis_showscale=False,
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f5f0ff"),
                              margin=dict(t=30, b=10), xaxis_title="", yaxis_title="Média de Pedidos")
            st.plotly_chart(fig, use_container_width=True, key="chart_top_faixas")

        with col_b:
            st.markdown("### 🛒 Nível de Compra por Faixa Etária")
            nivel_faixa = (
                df_pub.groupby(["faixa", "classificacao"])
                .size().reset_index(name="total")
            )
            nivel_faixa["faixa"] = pd.Categorical(nivel_faixa["faixa"], categories=ORDEM_FAIXAS, ordered=True)
            nivel_faixa = nivel_faixa.sort_values("faixa")

            fig = px.bar(nivel_faixa, x="faixa", y="total", color="classificacao",
                         color_discrete_map=CORES_NIVEL, barmode="stack", text="total")
            fig.update_traces(texttemplate="%{text:,}", textposition="inside",
                              hovertemplate="<b>%{x}</b> · %{fullData.name}<br>Clientes: %{y:,}<extra></extra>")
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                              font=dict(color="#3d2e6b", family="Sora"),
                              legend=dict(title="", orientation="h", y=-0.2),
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f5f0ff"),
                              margin=dict(t=30, b=80), xaxis_title="", yaxis_title="Clientes")
            st.plotly_chart(fig, use_container_width=True, key="chart_nivel_faixa")

        st.markdown("<br>", unsafe_allow_html=True)

        # Evolução do público ao longo do tempo
        st.markdown("### 📅 Evolução do Público por Faixa Etária")
        df_tempo = df_pub.dropna(subset=["atualizado_em"]).copy()
        df_tempo["mes"] = df_tempo["atualizado_em"].dt.to_period("M").astype(str)

        evolucao_faixa = (
            df_tempo.groupby(["mes", "faixa"])
            .size().reset_index(name="total")
        )
        evolucao_faixa["faixa"] = pd.Categorical(evolucao_faixa["faixa"], categories=ORDEM_FAIXAS, ordered=True)
        ultimos_meses = sorted(evolucao_faixa["mes"].unique())[-24:]
        evolucao_faixa = evolucao_faixa[evolucao_faixa["mes"].isin(ultimos_meses)]

        fig = px.line(evolucao_faixa, x="mes", y="total", color="faixa",
                      color_discrete_map=CORES_FAIXAS, markers=True, line_shape="spline")
        fig.update_traces(marker=dict(size=5, line=dict(color="white", width=1)),
                          hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>Clientes: %{y:,}<extra></extra>")
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          font=dict(color="#3d2e6b", family="Sora"),
                          legend=dict(title="Faixa Etária", orientation="h", y=-0.2),
                          xaxis=dict(tickangle=-45, showgrid=False),
                          yaxis=dict(gridcolor="#f5f0ff"),
                          margin=dict(t=20, b=80), xaxis_title="", yaxis_title="Novos Clientes")
        st.plotly_chart(fig, use_container_width=True, key="chart_evolucao_faixa")

    # ----------------------------------------------------------
    # RODAPÉ
    # ----------------------------------------------------------

    st.divider()
    st.markdown("<p style='text-align:center; color:#ddd; font-size:0.78rem'>Evolution Nutrition Lab · Dashboard de Clientes · Dados via API Olist</p>",
                unsafe_allow_html=True)

# ============================================================
# EXECUÇÃO
# ============================================================

if verificar_login():
    mostrar_dashboard()
