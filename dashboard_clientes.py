import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ============================================================
# CONFIGURAÇÕES
# ============================================================

ARQUIVO_CSV = r"C:\Users\Gustavo\OneDrive - GRUPO TSC\Área de Trabalho\OlistPython\Rel_Clientes\Clientes_csv\clientes_processado.csv"

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Clientes | Evolution Nutrition",
    page_icon="💚",
    layout="wide"
)

# CSS personalizado
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Sora', sans-serif;
        }
        .main { background-color: #0f1117; }

        .metric-card {
            background: linear-gradient(135deg, #1a1f2e, #232938);
            border: 1px solid #2a3045;
            border-radius: 16px;
            padding: 24px;
            text-align: center;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #4ade80;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #8892a4;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        h1 { color: #f1f5f9 !important; }
        h2, h3 { color: #cbd5e1 !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

@st.cache_data
def carregar_dados():
    df = pd.read_csv(ARQUIVO_CSV, encoding="utf-8-sig")
    df["atualizado_em"] = pd.to_datetime(df["atualizado_em"], format="%d/%m/%Y %H:%M", errors="coerce")
    df["ultimo_pedido_confirmado"] = pd.to_datetime(df["ultimo_pedido_confirmado"], format="%d/%m/%Y %H:%M", errors="coerce")
    return df

df = carregar_dados()

# ============================================================
# HEADER
# ============================================================

st.markdown("## 💚 Dashboard de Clientes")
st.markdown("**Evolution Nutrition Lab** — Análise da base de clientes")
st.divider()

# ============================================================
# MÉTRICAS PRINCIPAIS
# ============================================================

total         = len(df)
compraram     = df[df["pedidos_confirmados"] > 0]
recorrentes   = df[df["pedidos_confirmados"] >= 2]
cancelados    = df[(df["pedidos_confirmados"] == 0) & (df["pedidos_cancelados"] > 0)]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total:,}</div>
            <div class="metric-label">Total de Clientes</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(compraram):,}</div>
            <div class="metric-label">Compraram ao menos 1x</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(recorrentes):,}</div>
            <div class="metric-label">Clientes Recorrentes</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(cancelados):,}</div>
            <div class="metric-label">Só Cancelamentos</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# LINHA 1: PIZZA + BARRAS POR ESTADO
# ============================================================

col_esq, col_dir = st.columns(2)

with col_esq:
    st.markdown("### 🎯 Classificação de Clientes")
    ordem = ["1ª Compra", "2ª Compra", "3ª Compra", "4ª Compra", "5ª Compra +"]
    contagem = df["classificacao"].value_counts().reindex(ordem).reset_index()
    contagem.columns = ["classificacao", "total"]

    cores = ["#4ade80", "#22d3ee", "#818cf8", "#f472b6", "#fb923c"]
    fig_pizza = px.pie(
        contagem,
        names="classificacao",
        values="total",
        color_discrete_sequence=cores,
        hole=0.45
    )
    fig_pizza.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Sora"),
        legend=dict(font=dict(color="#cbd5e1")),
        margin=dict(t=20, b=20)
    )
    fig_pizza.update_traces(textfont_color="white", textinfo="percent+label")
    st.plotly_chart(fig_pizza, use_container_width=True)

with col_dir:
    st.markdown("### 🗺️ Clientes por Estado")
    estados = df["estado"].dropna()
    estados = estados[estados.str.strip() != ""]
    top_estados = estados.value_counts().head(15).reset_index()
    top_estados.columns = ["estado", "total"]

    fig_estados = px.bar(
        top_estados,
        x="total",
        y="estado",
        orientation="h",
        color="total",
        color_continuous_scale=["#1a3a2a", "#4ade80"],
    )
    fig_estados.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Sora"),
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending"),
        margin=dict(t=20, b=20),
        xaxis=dict(gridcolor="#2a3045"),
        yaxis_title="",
        xaxis_title="Clientes"
    )
    st.plotly_chart(fig_estados, use_container_width=True)

# ============================================================
# LINHA 2: EVOLUÇÃO MENSAL + TOP CIDADES
# ============================================================

col_esq2, col_dir2 = st.columns(2)

with col_esq2:
    st.markdown("### 📈 Novos Clientes por Mês")
    df_mes = df.dropna(subset=["atualizado_em"]).copy()
    df_mes["mes"] = df_mes["atualizado_em"].dt.to_period("M").astype(str)
    evolucao = df_mes.groupby("mes").size().reset_index(name="total")
    evolucao = evolucao.tail(24)  # últimos 24 meses

    fig_linha = px.line(
        evolucao,
        x="mes",
        y="total",
        markers=True,
        line_shape="spline"
    )
    fig_linha.update_traces(
        line_color="#4ade80",
        marker=dict(color="#4ade80", size=6),
        fill="tozeroy",
        fillcolor="rgba(74, 222, 128, 0.1)"
    )
    fig_linha.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Sora"),
        xaxis=dict(gridcolor="#2a3045", tickangle=-45),
        yaxis=dict(gridcolor="#2a3045"),
        margin=dict(t=20, b=60),
        xaxis_title="",
        yaxis_title="Clientes"
    )
    st.plotly_chart(fig_linha, use_container_width=True)

with col_dir2:
    st.markdown("### 🏙️ Top 15 Cidades")
    cidades = df["cidade"].dropna()
    cidades = cidades[cidades.str.strip() != ""]
    top_cidades = cidades.value_counts().head(15).reset_index()
    top_cidades.columns = ["cidade", "total"]

    fig_cidades = px.bar(
        top_cidades,
        x="total",
        y="cidade",
        orientation="h",
        color="total",
        color_continuous_scale=["#1a2a3a", "#22d3ee"],
    )
    fig_cidades.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Sora"),
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending"),
        margin=dict(t=20, b=20),
        xaxis=dict(gridcolor="#2a3045"),
        yaxis_title="",
        xaxis_title="Clientes"
    )
    st.plotly_chart(fig_cidades, use_container_width=True)

# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.markdown(
    "<p style='text-align:center; color:#4a5568; font-size:0.8rem;'>Evolution Nutrition Lab · Dashboard de Clientes · Dados via API Olist</p>",
    unsafe_allow_html=True
)
