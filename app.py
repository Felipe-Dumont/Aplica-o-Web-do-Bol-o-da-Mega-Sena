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

# CSS para estilização
st.markdown("""
<style>
    .numero-selecionado-badge {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        width: 40px;
        height: 40px;
        line-height: 40px;
        border-radius: 50%;
        margin: 5px;
        font-weight: bold;
        text-align: center;
    }
    
    .numeros-selecionados-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #4CAF50 !important;
        color: white !important;
        border: none !important;
        width: 100% !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

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
    
    # Sidebar para informações de pagamento
    with st.sidebar:
        st.header("💰 Dados para Pagamento")
        st.write(f"Valor da Cota: R$ {ParticipanteService.VALOR_COTA:.2f}")
        
        with st.expander("📱 Pagar com PIX", expanded=True):
            st.markdown("""
                ### Chave PIX
                ```
                12345678900
                ```
                **Tipo:** CPF
                
                ### Dados do Beneficiário
                **Nome:** João da Silva
                **Banco:** NuBank
            """)
    
    # Formulário de cadastro
    with st.form("novo_participante", clear_on_submit=True):
        nome = st.text_input("Nome do Participante")
        status_pagamento = st.selectbox(
            "Status do Pagamento",
            options=["Pendente", "Pago", "Confirmado"],
            index=0
        )
        
        # Seleção de números
        numeros_disponiveis = list(range(1, 61))
        numeros_selecionados = st.multiselect(
            "Selecione 6 números:",
            options=numeros_disponiveis,
            default=[],
            max_selections=6,
            format_func=lambda x: f"{x:02d}"
        )
        
        # Exibir números selecionados
        if numeros_selecionados:
            st.markdown(
                """
                <div class="numeros-selecionados-container">
                    <h4>Números selecionados:</h4>
                    """ +
                "".join([f'<span class="numero-selecionado-badge">{num:02d}</span>' 
                         for num in sorted(numeros_selecionados)]) +
                "</div>",
                unsafe_allow_html=True
            )
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            limpar = st.form_submit_button("🎲 Limpar Seleção", type="secondary")
        
        with col2:
            submitted = st.form_submit_button("✅ Adicionar Participante", type="primary")
        
        if submitted:
            if not nome:
                st.error("Por favor, preencha o nome do participante!")
            elif len(numeros_selecionados) != 6:
                st.error("Por favor, escolha exatamente 6 números!")
            else:
                novo_participante = Participante(
                    nome=nome,
                    valor_pago=ParticipanteService.VALOR_COTA,
                    numeros_escolhidos=numeros_selecionados,
                    status_pagamento=status_pagamento
                )
                
                if ParticipanteService.adicionar_participante(novo_participante):
                    st.success("Participante adicionado com sucesso!")
                    st.rerun()

elif pagina == "📋 Participantes":
    import pages.participantes as participantes
    participantes.app()

elif pagina == "🎯 Resultado":
    import pages.resultado_sorteio as resultado
    resultado.app()