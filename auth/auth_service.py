import streamlit as st
from config.database import get_db
import hashlib
import os

class AuthService:
    @staticmethod
    def init_auth_table():
        with get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS auth_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    access_code_hash TEXT NOT NULL
                )
            """)
            
            # Verifica se já existe um código de acesso
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM auth_config")
            if cursor.fetchone()[0] == 0:
                # Código padrão inicial: "admin123"
                default_code_hash = hashlib.sha256("algumasenhaaqui".encode()).hexdigest()
                conn.execute("INSERT INTO auth_config (access_code_hash) VALUES (?)", (default_code_hash,))
            conn.commit()

    @staticmethod
    def verify_access_code(code: str) -> bool:
        # Se já estiver autenticado pelo cookie, retorna True
        if st.session_state.get('_cookie_auth_status'):
            return True
            
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT access_code_hash FROM auth_config LIMIT 1")
            result = cursor.fetchone()
            return result and result[0] == code_hash

    @staticmethod
    def change_access_code(new_code: str) -> bool:
        new_code_hash = hashlib.sha256(new_code.encode()).hexdigest()
        with get_db() as conn:
            conn.execute("UPDATE auth_config SET access_code_hash = ?", (new_code_hash,))
            conn.commit()
            # Limpa o cookie de autenticação ao mudar a senha
            st.session_state['_cookie_auth_status'] = False
            return True

    @staticmethod
    def logout():
        st.session_state.authentication_status = False
        st.session_state['_cookie_auth_status'] = False 