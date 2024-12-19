import streamlit as st
from auth.auth_service import AuthService

def show_login_page():
    st.title("🔐 Login")
    
    # Verifica se já está autenticado
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        st.success("Você já está autenticado!")
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.rerun()
        return True
    
    # Formulário de login
    with st.form("login_form"):
        access_code = st.text_input("Código de Acesso", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            if AuthService.verify_access_code(access_code):
                st.session_state.authenticated = True
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Código de acesso inválido!")
    
    return False

def require_auth():
    if not show_login_page():
        st.stop() 