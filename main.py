import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy.stats import poisson
import sqlite3
import streamlit as st


st.write("Main iniciou")

if st.button("Ir pro login"):
    st.switch_page("pages/login.py")
# =====================================================
# 🔥 ESCONDER PÁGINAS
# =====================================================
hide_pages = """
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(hide_pages, unsafe_allow_html=True)

# =====================================================
# 🔐 PROTEÇÃO DE LOGIN
# =====================================================
if "user" not in st.session_state:
    st.warning("Você precisa estar logado.")
    st.switch_page("login")
    st.stop()

# =====================================================
# 🔌 CONEXÃO
# =====================================================
def conectar():
    return sqlite3.connect("futebol.db", check_same_thread=False)

user = st.session_state.user

# =====================================================
# ⚙️ CONFIG
# =====================================================
st.set_page_config(page_title="Dashboard Futebol", layout="wide")
st.title("⚽ Dashboard Histórico de Futebol")

# =====================================================
# 👤 SIDEBAR
# =====================================================
st.sidebar.write(f"👤 {user['nome']}")

if st.sidebar.button("Sair"):
    st.session_state.clear()
    st.switch_page("pages/login.py")

# =====================================================
# 📊 LIGAS E TEMPORADAS
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

# =====================================================
# ⭐ BUSCAR TIME FAVORITO (COM LIGA)
# =====================================================
conn = conectar()
cursor = conn.cursor()

cursor.execute(
    "SELECT nome, liga FROM times WHERE id = ?",
    (user["time_id"],)
)

resultado = cursor.fetchone()
conn.close()

time_padrao = None
liga_padrao = None

if resultado:
    time_padrao = resultado[0]
    liga_padrao = resultado[1]

# =====================================================
# 🔁 DEFINIR LIGA PADRÃO
# =====================================================
if liga_padrao:
    liga_nome = next((k for k, v in ligas.items() if v == liga_padrao), list(ligas.keys())[0])
else:
    liga_nome = list(ligas.keys())[0]

# =====================================================
# ⭐ BOTÃO FAVORITO
# =====================================================
if st.button("⭐ Ir para meu time favorito"):
    if time_padrao and liga_padrao:

        # Descobrir nome da liga (texto)
        liga_nome = next(
            (k for k, v in ligas.items() if v == liga_padrao),
            None
        )

        if liga_nome:
            st.session_state["liga"] = liga_nome
            st.session_state["time"] = time_padrao
            st.rerun()
# =====================================================
# 🎯 SELECT LIGA
# =====================================================
if "liga" not in st.session_state:
    st.session_state["liga"] = liga_nome

liga = st.selectbox(
    "Selecione a Liga",
    list(ligas.keys()),
    key="liga"
)

temporada = st.selectbox("Selecione a Temporada", temporadas.keys())

codigo_liga = ligas[liga]
codigo_temp = temporadas[temporada]



# =====================================================
# 📥 CARREGAR DADOS
# =====================================================
url = f"https://www.football-data.co.uk/mmz4281/{codigo_temp}/{codigo_liga}.csv"

@st.cache_data
def carregar_csv(url):
    df = pd.read_csv(url)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df

df = carregar_csv(url)

st.success("✅ Dados carregados com sucesso!")

# =====================================================
# ⚽ TIMES DISPONÍVEIS
# =====================================================
times_disponiveis = sorted(df["HomeTeam"].unique())

# =====================================================
# 🔥 DEFINIR TIME FINAL
# =====================================================
if "time" in st.session_state and st.session_state["time"] in times_disponiveis:
    time_padrao_final = st.session_state["time"]
elif time_padrao in times_disponiveis:
    time_padrao_final = time_padrao
else:
    time_padrao_final = times_disponiveis[0]

# =====================================================
# 🎯 SELECT TIME
# =====================================================
if "time" not in st.session_state:
    st.session_state["time"] = time_padrao_final

time = st.selectbox(
    "Selecione o Time para Análise Individual",
    times_disponiveis,
    key="time"
)

# =====================================================
# 📊 FILTRO
# =====================================================
df_time = df[
    (df["HomeTeam"] == time) |
    (df["AwayTeam"] == time)
].copy()

if df_time.empty:
    st.error("❌ Time não encontrado nessa liga.")
    st.stop()

df_time = df_time.sort_values("Date")

# =====================================================
# 📈 MÉTRICAS
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
# 📊 KPIs
# =====================================================
st.subheader(f"📊 Desempenho do {time} na temporada {temporada}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📅 Jogos", total_jogos)
col2.metric("⚽ Gols Marcados", total_gols)
col3.metric("📈 Média por Jogo", media_gols)
col4.metric("🏆 % de Vitórias", f"{percentual_vitorias}%")

st.divider()

# =====================================================
# 📉 GRÁFICO
# =====================================================
fig = px.line(
    df_time,
    x="Date",
    y="Pontos Acumulados",
    markers=True,
    title="🏆 Evolução dos Pontos"
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABELA FINAL
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

# =====================================================
# 🔮 PREVISÃO DE CONFRONTO (MODELO POISSON) COM JANELA PONDERADA
# =====================================================

import numpy as np
from scipy.stats import poisson

st.divider()
st.header("🔮 Previsão de Confronto (Modelo Poisson)")

col1, col2 = st.columns(2)
timeA = col1.selectbox("Time da Casa", times_disponiveis, key="prevA")
timeB = col2.selectbox("Time Visitante", times_disponiveis, key="prevB")

# =====================================================
# PARÂMETRO DE JANELA
# =====================================================
janela = st.slider("Número de jogos para análise", min_value=3, max_value=15, value=5, step=1)

# =====================================================
# FUNÇÃO PARA PEGAR ÚLTIMOS JOGOS
# =====================================================

def ultimos_jogos_time(time_nome, n_jogos):
    df_t = df[(df["HomeTeam"] == time_nome) | (df["AwayTeam"] == time_nome)].copy()
    df_t = df_t.sort_values("Date", ascending=False).head(n_jogos)

    df_t["Gols Marcados"] = df_t.apply(lambda row: row["FTHG"] if row["HomeTeam"] == time_nome else row["FTAG"], axis=1)
    df_t["Gols Sofridos"] = df_t.apply(lambda row: row["FTAG"] if row["HomeTeam"] == time_nome else row["FTHG"], axis=1)
    df_t["Resultado"] = df_t.apply(
        lambda row: "Vitória" if row["Gols Marcados"] > row["Gols Sofridos"]
        else "Empate" if row["Gols Marcados"] == row["Gols Sofridos"]
        else "Derrota", axis=1
    )
    return df_t

dfA = ultimos_jogos_time(timeA, janela)
dfB = ultimos_jogos_time(timeB, janela)

# =====================================================
# MOSTRAR ÚLTIMOS JOGOS
# =====================================================

st.subheader(f"📋 Últimos {janela} jogos")
col1, col2 = st.columns(2)
tabelaA = dfA[["Date","HomeTeam","AwayTeam","Gols Marcados","Gols Sofridos","Resultado"]].copy()
tabelaB = dfB[["Date","HomeTeam","AwayTeam","Gols Marcados","Gols Sofridos","Resultado"]].copy()
tabelaA["Date"] = tabelaA["Date"].dt.strftime("%d/%m/%Y")
tabelaB["Date"] = tabelaB["Date"].dt.strftime("%d/%m/%Y")
col1.markdown(f"### {timeA}")
col1.dataframe(tabelaA, use_container_width=True)
col2.markdown(f"### {timeB}")
col2.dataframe(tabelaB, use_container_width=True)

# =====================================================
# MÉDIA PONDERADA DE GOLS
# =====================================================

def media_ponderada(gols):
    n = len(gols)
    pesos = np.arange(n, 0, -1)  # maior peso para jogos mais recentes
    return np.average(gols, weights=pesos)

media_gols_A = media_ponderada(dfA["Gols Marcados"])
media_sofridos_A = media_ponderada(dfA["Gols Sofridos"])
media_gols_B = media_ponderada(dfB["Gols Marcados"])
media_sofridos_B = media_ponderada(dfB["Gols Sofridos"])

# =====================================================
# GOLS ESPERADOS
# =====================================================

gols_esperados_A = (media_gols_A + media_sofridos_B) / 2
gols_esperados_B = (media_gols_B + media_sofridos_A) / 2

# =====================================================
# MATRIZ DE PROBABILIDADE DE PLACARES
# =====================================================

max_gols = 5
prob_matrix = []
for i in range(max_gols + 1):
    for j in range(max_gols + 1):
        prob = poisson.pmf(i, gols_esperados_A) * poisson.pmf(j, gols_esperados_B)
        prob_matrix.append({"Placar": f"{i} x {j}", "Probabilidade": prob*100, "Gols_A": i, "Gols_B": j})

df_poisson = pd.DataFrame(prob_matrix).sort_values("Probabilidade", ascending=False)
top5 = df_poisson.head(5)

# =====================================================
# PLACAR MAIS PROVÁVEL
# =====================================================

placar_top = top5.iloc[0]["Placar"]
st.subheader("⚽ Placar Mais Provável")
st.markdown(f"## 🏟️ {timeA} **{placar_top}** {timeB}")

# =====================================================
# TOP 5 PLACARES
# =====================================================

st.subheader("📊 Top 5 Placares Mais Prováveis")
tabela_poisson = top5[["Placar","Probabilidade"]].copy()
tabela_poisson["Probabilidade"] = tabela_poisson["Probabilidade"].round(2).astype(str) + "%"
st.dataframe(tabela_poisson, use_container_width=True)

# =====================================================
# PROBABILIDADE DE RESULTADO
# =====================================================

prob_vitoria_A = df_poisson[df_poisson["Gols_A"] > df_poisson["Gols_B"]]["Probabilidade"].sum()
prob_empate = df_poisson[df_poisson["Gols_A"] == df_poisson["Gols_B"]]["Probabilidade"].sum()
prob_vitoria_B = df_poisson[df_poisson["Gols_A"] < df_poisson["Gols_B"]]["Probabilidade"].sum()

st.subheader("📊 Probabilidade de Resultado")
col1, col2, col3 = st.columns(3)
col1.metric(f"🏠 Vitória {timeA}", f"{prob_vitoria_A:.1f}%")
col2.metric("🤝 Empate", f"{prob_empate:.1f}%")
col3.metric(f"✈️ Vitória {timeB}", f"{prob_vitoria_B:.1f}%")

# =====================================================
# OVER / UNDER 2.5
# =====================================================

df_poisson["Total_Gols"] = df_poisson["Gols_A"] + df_poisson["Gols_B"]
prob_over25 = df_poisson[df_poisson["Total_Gols"] >= 3]["Probabilidade"].sum()
prob_under25 = df_poisson[df_poisson["Total_Gols"] <= 2]["Probabilidade"].sum()

st.subheader("⚽ Over / Under 2.5 Gols")
col1, col2 = st.columns(2)
col1.metric("Over 2.5", f"{prob_over25:.1f}%")
col2.metric("Under 2.5", f"{prob_under25:.1f}%")

# =====================================================
# BTTS
# =====================================================

prob_btts = df_poisson[(df_poisson["Gols_A"] >= 1) & (df_poisson["Gols_B"] >= 1)]["Probabilidade"].sum()
prob_nao_btts = 100 - prob_btts

st.subheader("🥅 Ambos Marcam (BTTS)")
col1, col2 = st.columns(2)
col1.metric("Sim", f"{prob_btts:.1f}%")
col2.metric("Não", f"{prob_nao_btts:.1f}%")
