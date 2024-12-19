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
st.set_page_config(page_title="Bolão Mega da Virada", page_icon="🎲")

# Requer autenticação antes de continuar
require_auth()

# CSS atualizado para melhor estilização dos botões
st.markdown("""
<style>
    .numero-grid {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 8px;
        margin: 20px 0;
    }
    
    .stButton > button {
        width: 45px !important;
        height: 45px !important;
        border-radius: 50% !important;
        padding: 0px !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: white !important;
        color: #1f1f1f !important;
        border: 2px solid #4CAF50 !important;
    }
    
    .stButton > button:hover {
        background-color: #e8f5e9 !important;
        transform: scale(1.05);
        transition: all 0.2s ease;
    }
    
    .stButton > button[data-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
        border-color: #4CAF50 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
    }
    
    .numeros-selecionados-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    
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
    
    .contador-container {
        text-align: center;
        padding: 10px;
        margin-bottom: 15px;
        background-color: #e8f5e9;
        border-radius: 5px;
        font-weight: bold;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 0px !important;
        margin: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# Atualizar o título para indicar que é a página principal
st.title("🎲 Bolão Mega da Virada 2024 - Cadastro")

# Adicionar uma mensagem de navegação
st.sidebar.info("""
    👈 Use o menu lateral para:
    - Cadastrar novos participantes (página atual)
    - Visualizar lista completa de participantes
""")

# Sidebar para configurações e informações de pagamento
with st.sidebar:
    st.header("Configurações")
    valor_cota = st.number_input("Valor da Cota (R$)", min_value=1.0, value=10.0)
    
    # Adiciona separador
    st.markdown("---")
    
    # Seção de dados para pagamento
    st.header("💰 Dados para Pagamento")
    
    # Expander para PIX
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
            
            > **Importante:** Após o pagamento, envie o comprovante para confirmação.
            
            ### Como pagar:
            1. Abra seu app do banco
            2. Escolha pagar com PIX
            3. Cole a chave acima
            4. Digite o valor da sua cota
            5. Confirme os dados e pague
        """)
    
    # Mensagem de suporte
    st.markdown("---")
    st.markdown("""
        ### ❓ Precisa de ajuda?
        Entre em contato pelo WhatsApp:
        **📱 (11) 99999-9999**
    """)

# Formulário para adicionar participante
with st.form("novo_participante", clear_on_submit=True):
    st.subheader("Adicionar Novo Participante")
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Participante")
    with col2:
        valor_pago = st.number_input("Valor Pago (R$)", min_value=0.0, value=valor_cota)
    
    # Adicionar seleção de status de pagamento
    status_pagamento = st.selectbox(
        "Status do Pagamento",
        options=["Pendente", "Pago", "Confirmado"],
        index=0
    )

    # Inicializar números selecionados se não existir
    if 'numeros_selecionados' not in st.session_state:
        st.session_state.numeros_selecionados = set()

    # Contador de números selecionados
    st.markdown(
        f"""
        <div class="contador-container">
            Selecione {6 - len(st.session_state.numeros_selecionados)} números
            ({len(st.session_state.numeros_selecionados)}/6 selecionados)
        </div>
        """,
        unsafe_allow_html=True
    )

    # Grid de números
    for linha in range(6):
        cols = st.columns(10)
        for i in range(10):
            numero = linha * 10 + i + 1
            if numero <= 60:
                with cols[i]:
                    # Verifica se o número já está selecionado
                    is_selected = numero in st.session_state.numeros_selecionados
                    # Cria o botão com estilo condicional
                    if st.button(
                        str(numero),
                        key=f"btn_{numero}",
                        disabled=len(st.session_state.numeros_selecionados) >= 6 and not is_selected,
                        help="Clique para selecionar/desselecionar"
                    ):
                        if is_selected:
                            st.session_state.numeros_selecionados.remove(numero)
                        elif len(st.session_state.numeros_selecionados) < 6:
                            st.session_state.numeros_selecionados.add(numero)
                        st.rerun()

    # Exibir números selecionados
    if st.session_state.numeros_selecionados:
        numeros_ordenados = sorted(st.session_state.numeros_selecionados)
        st.markdown(
            """
            <div class="numeros-selecionados-container">
                <h4>Números selecionados:</h4>
                """ +
            "".join([f'<span class="numero-selecionado-badge">{num}</span>' 
                     for num in numeros_ordenados]) +
            "</div>",
            unsafe_allow_html=True
        )

    # Botões de ação em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        limpar = st.form_submit_button("🎲 Limpar Seleção", type="secondary")
        if limpar:
            st.session_state.numeros_selecionados = set()
            st.rerun()
    
    with col2:
        submitted = st.form_submit_button("✅ Adicionar Participante", type="primary")
        if submitted:
            if not nome:
                st.error("Por favor, preencha o nome do participante!")
            elif len(st.session_state.numeros_selecionados) != 6:
                st.error("Por favor, escolha exatamente 6 números!")
            else:
                novo_participante = Participante(
                    nome=nome,
                    valor_pago=valor_pago,
                    numeros_escolhidos=list(st.session_state.numeros_selecionados),
                    status_pagamento=status_pagamento
                )
                
                if ParticipanteService.adicionar_participante(novo_participante):
                    st.success("Participante adicionado com sucesso!")
                    st.session_state.numeros_selecionados = set()
                    st.rerun()

# Exibição dos participantes
participantes = ParticipanteService.listar_participantes()
if participantes:
    st.subheader("Lista de Participantes")
    
    # Convertendo para DataFrame para exibição
    df_participantes = pd.DataFrame([
        {
            'Nome': p.nome,
            'Valor_Pago': p.valor_pago,
            'Numeros_Escolhidos': str(sorted(p.numeros_escolhidos)),
            'Data_Pagamento': p.data_pagamento,
            'Status': p.status_pagamento
        }
        for p in participantes
    ])
    
    # Adicionar estilo condicional baseado no status
    def highlight_status(val):
        if val == 'Pago':
            return 'background-color: #90EE90'
        elif val == 'Confirmado':
            return 'background-color: #98FB98'
        elif val == 'Pendente':
            return 'background-color: #FFB6C6'
        return ''

    # Exibir DataFrame com estilo
    st.dataframe(
        df_participantes.style.applymap(
            highlight_status,
            subset=['Status']
        ),
        use_container_width=True
    )
    
    # Análise dos números
    st.subheader("Análise dos Números")
    
    numeros_repetidos = ParticipanteService.analisar_numeros_repetidos()
    if numeros_repetidos:
        st.warning("Números escolhidos por mais de uma pessoa:")
        for num, pessoas in numeros_repetidos.items():
            st.write(f"Número {num}: {', '.join(pessoas)}")
    
    # Estatísticas
    estatisticas = ParticipanteService.obter_estatisticas()
    st.subheader("Estatísticas")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Participantes", estatisticas['total_participantes'])
    with col2:
        st.metric("Total Arrecadado", f"R$ {estatisticas['total_arrecadado']:.2f}")

    # Botão para baixar dados
    st.download_button(
        label="Baixar dados em Excel",
        data=df_participantes.to_csv(index=False).encode('utf-8'),
        file_name='bolao_mega_sena.csv',
        mime='text/csv'
    )