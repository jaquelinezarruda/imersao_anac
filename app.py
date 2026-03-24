import pandas as pd
import streamlit as st
import plotly.express as px


# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard Dados Setor Aéreo",
    page_icon="📊",
    layout="wide",
)
# --- Carregamento dos dados ---
df = pd.read_csv("data/df_limpo.csv", sep = ',')

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ANO'].unique())
anos_selecionados = st.sidebar.multiselect("ANO", anos_disponiveis, default=anos_disponiveis)

# Filtro de Natureza de Voo
natureza_disponivel = sorted(df['NATUREZA'].unique())
natureza_selecionada = st.sidebar.multiselect("NATUREZA", natureza_disponivel, default=natureza_disponivel)

# Filtro de Grupo de Voo
grupo_disponivel = sorted(df['GRUPO DE VOO'].unique())
grupo_selecionado = st.sidebar.multiselect("GRUPO DE VOO", grupo_disponivel, default=grupo_disponivel)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ANO'].isin(anos_selecionados)) &
    (df['NATUREZA'].isin(natureza_selecionada)) &
    (df['GRUPO DE VOO'].isin(grupo_selecionado))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Dados do Setor Aéreo Brasileiro de 2015 a 2025")
st.markdown("Explore os dados do setor aéreo Brasileiro dos últimos 10 anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais")

if not df_filtrado.empty:
    passageiros_totais = (df_filtrado['PASSAGEIROS PAGOS'] + df_filtrado['PASSAGEIROS GRÁTIS']).sum()
    carga_total = (df_filtrado['CARGA PAGA (KG)'] + df_filtrado['CARGA GRÁTIS (KG)']).sum()
    natureza_mais_frequente = df_filtrado["NATUREZA"].mode()[0]
    soma_decolagens = df_filtrado["DECOLAGENS"].sum()
else:
    passageiros_totais, carga_total, natureza_mais_frequente, soma_decolagens = 0, 0, 0, 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Passageiros Transportados", f"{passageiros_totais:,.0f}".replace(",", "."))
col2.metric("Total de Carga Transportada (KG)", f"{carga_total:,.0f}".replace(",", "."))
col3.metric("Natureza mais frequente", natureza_mais_frequente)
col4.metric("Soma de Decolagens", f"{soma_decolagens:,.0f}".replace(",", "."))

st.markdown("---")


# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

#---- Passageiros Pagos por Ano: gráfico de barras

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        paxt = df_filtrado.groupby('ANO')['PASSAGEIROS PAGOS'].sum().sort_values(ascending=True).reset_index()
        grafico_passageiros = px.bar(
            paxt,
            x='ANO',
            y= 'PASSAGEIROS PAGOS',
            orientation='v',
            title="Passageiros Pagos Transportados",
            labels={'ANO': 'ano', 'PASSAGEIROS PAGOS': 'Passageiros'},
            color_discrete_sequence=['#0C2D48'] #--Cor das barras
        )
        grafico_passageiros.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_passageiros, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

#---- Carga Total por Ano: gráfico de barras

with col_graf2:
    if not df_filtrado.empty:
        carga_total = df_filtrado.groupby('ANO')['CARGA PAGA (KG)'].sum().sort_values(ascending=True).reset_index()
        grafico_carga = px.bar(
            carga_total,
            x='ANO',
            y= 'CARGA PAGA (KG)',
            orientation='v',
            title="Carga Paga (KG) Transportada",
            labels={'ANO': 'ano', 'CARGA PAGA (KG)': 'Carga (KG)'},
            color_discrete_sequence=['#0C2D48'] #--Cor das barras
        )
        grafico_carga.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_carga, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)


# ---- Grafico de Pizza de companhia

df_nacional = df_filtrado[df_filtrado['EMPRESA (NACIONALIDADE)'] == 'BRASILEIRA']

with col_graf3:
    df_nacional = df_filtrado[df_filtrado['EMPRESA (NACIONALIDADE)'] == 'BRASILEIRA']
    
    if not df_nacional.empty:
        #paxt_cia = df_nacional['EMPRESA (NOME)'].sum().reset_index()
        paxt_cia = df_filtrado.groupby('EMPRESA (NOME)')['PASSAGEIROS PAGOS'].sum().reset_index()
        paxt_cia.columns = ['EMPRESA (NOME)', 'PASSAGEIROS PAGOS']
        
        # --- LÓGICA PARA AGRUPAR "OUTRAS" ---
        total_voos = paxt_cia['PASSAGEIROS PAGOS'].sum()
        # Define quem tem menos de 2% do total
        limite = 0.02 
        paxt_cia['EMPRESA (NOME)'] = paxt_cia.apply(
            lambda x: x['EMPRESA (NOME)'] if (x['PASSAGEIROS PAGOS']/total_voos) > limite else 'OUTRAS', 
            axis=1
        )
        # Re-agrupa para somar tudo que virou 'OUTRAS'
        paxt_cia = paxt_cia.groupby('EMPRESA (NOME)')['PASSAGEIROS PAGOS'].sum().reset_index()
        # Ordena para o gráfico ficar bonito
        paxt_cia = paxt_cia.sort_values(by='PASSAGEIROS PAGOS', ascending=False)

        grafico_cias = px.pie(
            paxt_cia,
            names='EMPRESA (NOME)',
            values='PASSAGEIROS PAGOS',
            title='MarketShare CIAS Aéreas (Principais) por Passageiros Totais Trans.',
            hole=0.5,
            #color_discrete_sequence=px.colors.qualitative.Prism # Cores mais vibrantes
            color_discrete_sequence=['#2E86C1', '#5DADE2', '#85C1E9', '#ABB2B9', '#D5DBDB']
        )
        
        # Ajustes de layout para evitar sobreposição
        grafico_cias.update_traces(
            textinfo='percent', # Deixa apenas o percentual no gráfico
            textposition='inside', # Força o texto para dentro da fatia
            insidetextorientation='radial'
        )
        
        grafico_cias.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5) # Legenda embaixo
        )
        
        st.plotly_chart(grafico_cias, width='stretch')

with col_graf4:
    if not df_filtrado.empty:
        ask_rpk = df_filtrado.groupby('ANO')[['ASK', 'RPK']].sum().reset_index()
        grafico_ask_rpk = px.bar(
            ask_rpk,
            x='ANO',
            y=['ASK', 'RPK'],
            barmode='group',
            title='ASK vx RPK por Ano',
            labels={'': 'Total', 'ANO': 'ASK vx RPK'})
        grafico_ask_rpk.update_layout(title_x=0.1)
        st.plotly_chart(grafico_ask_rpk, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)