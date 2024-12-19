import streamlit as st
import pandas as pd
from datetime import datetime
from config.database import init_db
from models.participante import Participante
from services.participante_service import ParticipanteService
from auth.auth_service import AuthService
from pages.login import require_auth

# Inicialização do banco de dados e autenticação
init_db()
AuthService.init_auth_table()

# Configuração inicial da página
st.set_page_config(
    page_title="Bolão Mega da Virada",
    page_icon="🎲",
    layout="wide"
)

# Configurar navegação no sidebar
st.sidebar.title("Navegação")
pagina = st.sidebar.radio(
    "Ir para:",
    ["🎲 Cadastro", "📋 Participantes", "🎯 Resultado"],
    index=0
)

# Requer autenticação antes de continuar
require_auth()

# Navegação entre páginas
if pagina == "🎲 Cadastro":
    st.title("🎲 Bolão Mega da Virada 2024 - Cadastro")
    # ... resto do código do cadastro ...

elif pagina == "📋 Participantes":
    import pages.participantes as participantes
    participantes.app()

elif pagina == "🎯 Resultado":
    import pages.resultado_sorteio as resultado
    resultado.app()

# Remover a parte de listagem que estava aqui antes