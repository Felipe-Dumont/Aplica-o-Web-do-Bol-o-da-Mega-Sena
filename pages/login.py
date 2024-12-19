import streamlit as st
from auth.auth_service import AuthService
import time

def init_session_state():
    if 'authentication_status' not in st.session_state:
        # Tenta recuperar o status de autenticação do cookie
        if st.session_state.get('_cookie_auth_status'):
            st.session_state.authentication_status = True
        else:
            st.session_state.authentication_status = False

def show_login_page():
    init_session_state()
    
    # Verifica se já está autenticado
    if st.session_state.authentication_status:
        col1, col2 = st.columns([8, 2])
        with col2:
            if st.button("🚪 Sair"):
                st.session_state.authentication_status = False
                # Remove o cookie de autenticação
                st.session_state['_cookie_auth_status'] = False
                st.rerun()
        return True
    
    st.title("🔐 Login")
    
    # Formulário de login
    with st.form("login_form"):
        access_code = st.text_input("Código de Acesso", type="password")
        remember_me = st.checkbox("Manter conectado")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            if AuthService.verify_access_code(access_code):
                st.session_state.authentication_status = True
                if remember_me:
                    # Salva o status de autenticação no cookie
                    st.session_state['_cookie_auth_status'] = True
                st.success("Login realizado com sucesso!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Código de acesso inválido!")
    
    return False

def require_auth():
    if not show_login_page():
        st.stop() 