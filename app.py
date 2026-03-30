import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ── CONFIGURAÇÃO DA PÁGINA ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cartões GovBR",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILOS CUSTOMIZADOS (CSS DARK MODE & ESPAÇAMENTO) ────────────────────────
st.markdown("""
<style>
    /* Esconde o menu e o rodapé padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Estilo para os cartões de métricas (Cards) - Mais espaçados e Dark */
    div[data-testid="metric-container"] {
        background-color: #262730; /* Fundo escuro do card */
        border: 1px solid #3f3f4e; /* Borda sutil */
        padding: 20px 25px; /* Mais espaço interno (respiro) */
        border-radius: 12px; /* Bordas mais suaves */
        box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.4); /* Sombra para dar profundidade */
        border-left: 6px solid #00D2FF; /* Detalhe azul neon lateral */
        margin-bottom: 1rem; /* Espaço abaixo dos cards */
    }

    /* Afasta um pouco as colunas das métricas */
    div[data-testid="stHorizontalBlock"] {
        gap: 1.5rem; 
    }
</style>
""", unsafe_allow_html=True)

# ── CAMINHOS DOS DADOS ────────────────────────────────────────────────────────
PASTA_DADOS = "src/data/processed/tabelas"


@st.cache_data
def carregar_dados(nome_arquivo):
    caminho = os.path.join(PASTA_DADOS, f"{nome_arquivo}.csv")
    try:
        return pd.read_csv(caminho)
    except FileNotFoundError:
        return pd.DataFrame()


# ── BARRA LATERAL (MENU) ──────────────────────────────────────────────────────
st.sidebar.title("💳 Cartões GovBR")
st.sidebar.markdown("Análise de gastos com cartões de pagamento do Governo Federal.")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navegação",
    ["Visão Geral", "Rankings", "Análise Temporal", "Anomalias", "Mapa"]
)

st.sidebar.divider()
st.sidebar.info("Dados extraídos do Portal da Transparência.")

# ── PÁGINAS ───────────────────────────────────────────────────────────────────

# ==========================================
# PÁGINA 1: VISÃO GERAL
# ==========================================
if menu == "Visão Geral":
    st.title("📊 Visão Geral dos Gastos")
    st.markdown("Monitoramento consolidado das despesas (2024).")
    st.write("")  # Espaçador

    df_resumo = carregar_dados("resumo_geral")

    if not df_resumo.empty:
        resumo = dict(zip(df_resumo["metrica"], df_resumo["valor"]))

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_gasto = float(resumo.get("total_gasto", 0))
            st.metric("Total Gasto", f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with col2:
            st.metric("Total de Transações", f"{int(float(resumo.get('total_registros', 0))):,}".replace(",", "."))
        with col3:
            ticket_medio = float(resumo.get("ticket_medio", 0))
            st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with col4:
            st.metric("Órgãos Envolvidos",
                      f"{int(float(resumo.get('total_unidades_gestoras', 0))):,}".replace(",", "."))

        st.divider()

        df_mes = carregar_dados("gastos_por_mes")
        if not df_mes.empty:
            df_mes["mes"] = df_mes["mes"].astype(str)
            fig = px.area(
                df_mes, x="mes", y="total_gasto",
                labels={"mes": "Mês", "total_gasto": "Total Gasto (R$)"},
                title="Evolução Mensal de Despesas",
                color_discrete_sequence=["#00D2FF"],
                template="plotly_dark"
            )
            fig.update_layout(xaxis_type='category', margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# PÁGINA 2: RANKINGS
# ==========================================
elif menu == "Rankings":
    st.title("🏆 Rankings de Gastos")
    st.markdown("Visualização direta de quem mais gasta e quem mais recebe.")
    st.write("")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        df_ug = carregar_dados("top_unidades_gestoras")
        if not df_ug.empty:
            df_ug_chart = df_ug.head(10).sort_values("total_gasto", ascending=True)
            fig1 = px.bar(
                df_ug_chart, x="total_gasto", y="ug_nome", orientation='h',
                title="Top 10 Órgãos (Unidades Gestoras)",
                labels={"ug_nome": "", "total_gasto": "Valor (R$)"},
                color_discrete_sequence=["#00D2FF"],
                template="plotly_dark"
            )
            fig1.update_layout(margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        df_estab = carregar_dados("top_estabelecimentos")
        if not df_estab.empty:
            df_estab_chart = df_estab.head(10).sort_values("total_gasto", ascending=True)
            fig2 = px.bar(
                df_estab_chart, x="total_gasto", y="estab_nome", orientation='h',
                title="Top 10 Fornecedores (Estabelecimentos)",
                labels={"estab_nome": "", "total_gasto": "Valor (R$)"},
                color_discrete_sequence=["#FF3366"],
                template="plotly_dark"
            )
            fig2.update_layout(margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# PÁGINA 3: ANÁLISE TEMPORAL
# ==========================================
elif menu == "Análise Temporal":
    st.title("📆 Comportamento Temporal")
    st.markdown("Análise de padrões de consumo ao longo dos dias.")
    st.write("")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        df_dia_semana = carregar_dados("gastos_por_dia_semana")
        if not df_dia_semana.empty:
            fig = px.bar(
                df_dia_semana, x="dia_semana", y="total_gasto",
                title="Gastos por Dia da Semana",
                labels={"dia_semana": "Dia da Semana", "total_gasto": "Total Gasto (R$)"},
                color="total_gasto",
                color_continuous_scale="blues",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_fds = carregar_dados("gastos_fim_semana_vs_semana")
        if not df_fds.empty:
            fig = px.pie(
                df_fds, values='total_gasto', names='fim_de_semana', hole=0.5,
                title="Dias Úteis vs Fim de Semana",
                color_discrete_sequence=["#00D2FF", "#FF3366"],
                template="plotly_dark"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# PÁGINA 4: ANOMALIAS (100% VISUAL)
# ==========================================
elif menu == "Anomalias":
    st.title("🚨 Análise de Anomalias")
    st.markdown("Detecção visual de padrões atípicos e transações suspeitas.")
    st.write("")

    # --- 1. TRANSAÇÕES DE ALTO VALOR ---
    df_alto = carregar_dados("transacoes_alto_valor")
    if not df_alto.empty:
        st.subheader("💎 Transações de Alto Valor (Outliers Principais)")

        # Garante que as colunas existam para não dar erro
        for col in ['estab_nome', 'valorTransacao', 'portador_nome', 'ug_nome', 'dataTransacao']:
            if col not in df_alto.columns:
                df_alto[col] = "N/A"

        # Ordena para pegar os maiores
        df_alto = df_alto.sort_values("valorTransacao", ascending=False)

        # O Gráfico de Dispersão limpo e customizado
        fig_scatter = px.scatter(
            df_alto, x="estab_nome", y="valorTransacao",
            size="valorTransacao", color="valorTransacao",
            color_continuous_scale="reds",
            template="plotly_dark"
        )

        # Tooltip limpo e direto
        fig_scatter.update_traces(
            customdata=df_alto[['estab_nome', 'valorTransacao', 'portador_nome', 'ug_nome']],
            hovertemplate="<br>".join([
                "<b>%{customdata[0]}</b>",
                "Valor: <b>R$ %{customdata[1]:,.2f}</b>",
                "Portador: %{customdata[2]}",
                "Órgão: %{customdata[3]}"
            ]) + "<extra></extra>"
        )
        fig_scatter.update_layout(xaxis={'visible': False, 'showticklabels': False}, margin=dict(t=0, b=0))
        st.plotly_chart(fig_scatter, use_container_width=True)

        # CARDS COM TODAS AS INFORMAÇÕES DOS TOP 3 (Foco total no visual)
        st.markdown("### 🔍 Top 3 Maiores Anomalias (Raio-X)")
        top3 = df_alto.head(3)
        cols_top = st.columns(3)
        for i, (index, row) in enumerate(top3.iterrows()):
            with cols_top[i]:
                # HTML/CSS para criar um card premium que combina com o tema Dark
                st.markdown(f"""
                <div style="background-color: #262730; padding: 20px; border-radius: 12px; border-top: 5px solid #FF3366; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); height: 100%;">
                    <h3 style="color: #00D2FF; margin-top: 0; font-size: 24px;">R$ {row['valorTransacao']:,.2f}</h3>
                    <p style="margin-bottom: 8px; font-size: 15px;">🏢 <b>Local:</b> {row['estab_nome']}</p>
                    <p style="margin-bottom: 8px; font-size: 14px; color: #CCCCCC;">👤 <b>Portador:</b> {row['portador_nome']}</p>
                    <p style="margin-bottom: 8px; font-size: 14px; color: #CCCCCC;">🏛️ <b>Órgão:</b> {row['ug_nome']}</p>
                    <p style="margin-bottom: 0px; font-size: 14px; color: #CCCCCC;">📅 <b>Data:</b> {row['dataTransacao']}</p>
                </div>
                """, unsafe_allow_html=True)

    st.divider()

    # --- 2. ESTABELECIMENTOS DE ATENÇÃO E FRAGMENTADAS ---
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("🔞 Locais de Atenção")
        st.markdown("<span style='color:#aaa; font-size:14px;'>Estabelecimentos incomuns e valores recebidos.</span>",
                    unsafe_allow_html=True)
        df_incomum = carregar_dados("estabelecimentos_incomuns")
        if not df_incomum.empty:
            df_inc_chart = df_incomum.head(15).sort_values("valorTransacao", ascending=True)
            # Gráfico de barras horizontais
            fig_inc = px.bar(
                df_inc_chart, x="valorTransacao", y="estab_nome", orientation='h',
                color_discrete_sequence=["#FF3366"],
                template="plotly_dark",
                text_auto=".2s"
            )
            fig_inc.update_layout(xaxis_title="", yaxis_title="", margin=dict(l=0, r=0, t=20, b=0))
            fig_inc.update_traces(hovertemplate="<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>")
            st.plotly_chart(fig_inc, use_container_width=True)

    with col2:
        st.subheader("🧩 Compras Fragmentadas")
        st.markdown("<span style='color:#aaa; font-size:14px;'>Relação visual: Portador → Estabelecimento.</span>",
                    unsafe_allow_html=True)
        df_frag = carregar_dados("compras_fragmentadas")
        if not df_frag.empty:
            if 'portador_nome' in df_frag.columns and 'estab_nome' in df_frag.columns:
                df_frag['portador_nome'] = df_frag['portador_nome'].fillna("Não Informado")
                df_frag['estab_nome'] = df_frag['estab_nome'].fillna("Não Informado")

                df_frag_chart = df_frag.head(50)

                # Treemap (Mapa de Árvore)
                fig_tree = px.treemap(
                    df_frag_chart,
                    path=[px.Constant("Fragmentações"), "portador_nome", "estab_nome"],
                    values="valorTransacao",
                    color="valorTransacao",
                    color_continuous_scale="Oranges",
                    template="plotly_dark"
                )
                fig_tree.update_traces(hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>")
                fig_tree.update_layout(margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig_tree, use_container_width=True)

# ==========================================
# PÁGINA 5: MAPA (DARK MODE)
# ==========================================
elif menu == "Mapa":
    st.title("🗺️ Distribuição Geográfica")
    st.write("")

    df_mapa = carregar_dados("cnpjs_enriquecidos")

    if not df_mapa.empty:
        col1, col2 = st.columns([3, 1], gap="large")

        with col2:
            st.subheader("Ranking por Estado")
            df_uf = df_mapa.groupby("uf")["valorTransacao"].sum().reset_index()
            df_uf = df_uf.sort_values("valorTransacao", ascending=False)
            df_uf_display = df_uf.copy()
            df_uf_display.columns = ["Estado", "Total (R$)"]
            st.dataframe(df_uf_display, hide_index=True, use_container_width=True)

        with col1:
            df_uf = df_mapa.groupby("uf")["valorTransacao"].sum().reset_index()
            url_geojson = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

            fig = px.choropleth(
                df_uf, geojson=url_geojson, featureidkey="properties.sigla",
                locations="uf", color="valorTransacao",
                color_continuous_scale="Viridis",
                title="Intensidade de Gasto por Estado",
                labels={'valorTransacao': 'Total Gasto (R$)'},
                template="plotly_dark"
            )
            fig.update_geos(fitbounds="locations", visible=False, bgcolor="#0E1117")
            fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

            st.plotly_chart(fig, use_container_width=True)