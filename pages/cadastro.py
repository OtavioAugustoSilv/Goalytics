import streamlit as st
from bd.bd_User import criar_usuario
from bd.db_connection import conectar

st.set_page_config(page_title="Cadastro", layout="centered")
hide_pages = """
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(hide_pages, unsafe_allow_html=True)
st.title("📝 Cadastro de Usuário")

# 🔹 Buscar times do banco
def buscar_times():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome FROM times ORDER BY nome")
    times = cursor.fetchall()

    conn.close()
    return times

times = buscar_times()

# 🔹 Inputs
nome = st.text_input("Nome")
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

# 🔹 Select de time
if times:
    nomes_times = [t[1] for t in times]
    time_escolhido = st.selectbox("Time favorito", nomes_times)

    # pega o ID do time selecionado
    time_id = next(t[0] for t in times if t[1] == time_escolhido)
else:
    st.error("Nenhum time encontrado no banco.")
    st.stop()

# 🔹 Botão cadastrar
if st.button("Cadastrar"):
    if not nome or not email or not senha:
        st.warning("Preencha todos os campos!")
    else:
        sucesso = criar_usuario(nome, email, senha, time_id)

        if sucesso:
            st.success("✅ Cadastro realizado com sucesso!")
            st.switch_page("pages/login.py")
        else:
            st.error("❌ Email já cadastrado")

# 🔹 Link para login
st.markdown("---")
if st.button("Já tenho conta"):
    st.switch_page("pages/login.py")