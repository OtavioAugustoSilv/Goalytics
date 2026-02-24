import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Futebol Histórico", layout="wide")
st.title("⚽ Dashboard Histórico de Futebol")

# =====================================================
# ESCOLHER LIGA E TEMPORADA
# =====================================================

ligas = {
    "Premier League (Inglaterra)": "E0",
    "La Liga (Espanha)": "SP1",
    "Bundesliga (Alemanha)": "D1"
}

temporadas = {
    "2023-2024": "2324",
    "2022-2023": "2223",
    "2021-2022": "2122"
}

liga = st.selectbox("Selecione a Liga", ligas.keys())
temporada = st.selectbox("Selecione a Temporada", temporadas.keys())

codigo_liga = ligas[liga]
codigo_temp = temporadas[temporada]

url = f"https://www.football-data.co.uk/mmz4281/{codigo_temp}/{codigo_liga}.csv"

@st.cache_data
def carregar_csv(url):
    df = pd.read_csv(url)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df

df = carregar_csv(url)

st.success("✅ Dados carregados com sucesso!")

# =====================================================
# FILTRAR TIME
# =====================================================

# =====================================================
# FILTRAR TIME (DROPDOWN)
# =====================================================

times_disponiveis = sorted(df["HomeTeam"].unique())

time = st.selectbox(
    "Selecione o Time para Análise Individual",
    times_disponiveis
)

df_time = df[
    (df["HomeTeam"] == time) |
    (df["AwayTeam"] == time)
].copy()

if df_time.empty:
    st.error("❌ Time não encontrado nessa liga/temporada.")
    st.stop()

df_time = df_time.sort_values("Date")
df_time = df[
    (df["HomeTeam"] == time) |
    (df["AwayTeam"] == time)
].copy()

if df_time.empty:
    st.error("❌ Time não encontrado nessa liga/temporada.")
    st.stop()

df_time = df_time.sort_values("Date")

# =====================================================
# CÁLCULO DE MÉTRICAS
# =====================================================

df_time["Gols Marcados"] = df_time.apply(
    lambda row: row["FTHG"] if row["HomeTeam"] == time else row["FTAG"], axis=1
)

df_time["Gols Sofridos"] = df_time.apply(
    lambda row: row["FTAG"] if row["HomeTeam"] == time else row["FTHG"], axis=1
)

df_time["Resultado"] = df_time.apply(
    lambda row:
        "Vitória 🟢" if row["Gols Marcados"] > row["Gols Sofridos"]
        else "Empate 🟡" if row["Gols Marcados"] == row["Gols Sofridos"]
        else "Derrota 🔴",
    axis=1
)

df_time["Pontos"] = df_time["Resultado"].apply(
    lambda x: 3 if "Vitória" in x else 1 if "Empate" in x else 0
)

df_time["Pontos Acumulados"] = df_time["Pontos"].cumsum()

total_jogos = len(df_time)
total_gols = df_time["Gols Marcados"].sum()
media_gols = round(total_gols / total_jogos, 2)
percentual_vitorias = round(
    (len(df_time[df_time["Resultado"] == "Vitória 🟢"]) / total_jogos) * 100, 1
)

# =====================================================
# KPIs
# =====================================================

st.subheader(f"📊 Desempenho do {time} na temporada {temporada}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📅 Jogos", total_jogos)
col2.metric("⚽ Gols Marcados", total_gols)
col3.metric("📈 Média por Jogo", media_gols)
col4.metric("🏆 % de Vitórias", f"{percentual_vitorias}%")

st.divider()

# =====================================================
# GRÁFICO
# =====================================================

fig = px.line(
    df_time,
    x="Date",
    y="Pontos Acumulados",
    markers=True,
    title="🏆 Evolução dos Pontos na Temporada"
)

fig.update_layout(
    xaxis_title="Data",
    yaxis_title="Pontos Acumulados"
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABELA FINAL ORGANIZADA
# =====================================================

st.subheader("📋 Histórico de Jogos")

tabela = df_time[[
    "Date",
    "HomeTeam",
    "AwayTeam",
    "Gols Marcados",
    "Gols Sofridos",
    "Resultado",
    "Pontos Acumulados"
]].copy()

tabela.columns = [
    "Data",
    "Time da Casa",
    "Time Visitante",
    "Gols Marcados",
    "Gols Sofridos",
    "Resultado",
    "Pontos Acumulados"
]

tabela["Data"] = tabela["Data"].dt.strftime("%d/%m/%Y")

st.dataframe(tabela, use_container_width=True)

# =====================================================
# ⚔️ COMPARAÇÃO EM LINHA - MÚLTIPLAS MÉTRICAS
# =====================================================

st.divider()
st.header("📈 Comparação de Evolução na Temporada")

times_disponiveis = sorted(df["HomeTeam"].unique())

colA, colB = st.columns(2)
time1 = colA.selectbox("Selecione o Primeiro Time", times_disponiveis, key="t1")
time2 = colB.selectbox("Selecione o Segundo Time", times_disponiveis, key="t2")

metricas = st.multiselect(
    "Selecione as Métricas para Comparação",
    ["Pontos Acumulados", "Gols Marcados", "% Vitórias"],
    default=["Pontos Acumulados"]
)

def preparar_dados(time_nome):
    df_t = df[
        (df["HomeTeam"] == time_nome) |
        (df["AwayTeam"] == time_nome)
    ].copy()

    df_t = df_t.sort_values("Date").reset_index(drop=True)

    df_t["Gols Marcados"] = df_t.apply(
        lambda row: row["FTHG"] if row["HomeTeam"] == time_nome else row["FTAG"],
        axis=1
    )

    df_t["Gols Sofridos"] = df_t.apply(
        lambda row: row["FTAG"] if row["HomeTeam"] == time_nome else row["FTHG"],
        axis=1
    )

    df_t["Resultado"] = df_t.apply(
        lambda row:
            "Vitória" if row["Gols Marcados"] > row["Gols Sofridos"]
            else "Empate" if row["Gols Marcados"] == row["Gols Sofridos"]
            else "Derrota",
        axis=1
    )

    df_t["Pontos"] = df_t["Resultado"].apply(
        lambda x: 3 if x == "Vitória" else 1 if x == "Empate" else 0
    )

    df_t["Pontos Acumulados"] = df_t["Pontos"].cumsum()

    df_t["% Vitórias"] = (
        df_t["Resultado"].eq("Vitória").cumsum()
        / (df_t.index + 1)
    ) * 100

    df_t["Time"] = time_nome

    return df_t


df1 = preparar_dados(time1)
df2 = preparar_dados(time2)

df_comparacao = pd.concat([df1, df2])

if metricas:

    df_melt = df_comparacao.melt(
        id_vars=["Date", "Time"],
        value_vars=metricas,
        var_name="Métrica",
        value_name="Valor"
    )

    fig = px.line(
        df_melt,
        x="Date",
        y="Valor",
        color="Time",
        line_dash="Métrica",
        markers=True,
        title="📊 Comparação de Desempenho na Temporada"
    )

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Valor",
        legend_title="Times / Métricas"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Selecione pelo menos uma métrica.")