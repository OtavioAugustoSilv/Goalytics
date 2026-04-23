import streamlit as st
from bd.bd_User import buscar_usuario

st.set_page_config(page_title="Login", layout="centered")
hide_pages = """
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(hide_pages, unsafe_allow_html=True)
st.title("🔐 Login")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    if not email or not senha:
        st.warning("Preencha todos os campos!")
    else:
        user = buscar_usuario(email, senha)

        if user:
            st.success("✅ Login realizado com sucesso!")

            # salva usuário na sessão
            st.session_state["user"] = {
                "id": user[0],
                "nome": user[1],
                "email": user[2],
                "time_id": user[4]
            }

            st.switch_page("main.py")

        else:
            st.error("❌ Email ou senha inválidos")

# 🔹 Ir para cadastro
st.markdown("---")
if st.button("Criar conta"):
    st.switch_page("pages/cadastro.py")