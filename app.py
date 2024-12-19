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
    
    /* Estilo para os checkboxes */
    .stCheckbox {
        position: relative;
        padding: 5px;
        background-color: white;
        border-radius: 50%;
        border: 2px solid #4CAF50;
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 2px;
    }
    
    .stCheckbox:hover {
        background-color: #e8f5e9;
        transform: scale(1.05);
        transition: all 0.2s ease;
    }
    
    .stCheckbox [data-testid="stMarkdownContainer"] p {
        font-weight: bold;
        margin: 0;
        text-align: center;
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
    st.write(f"Valor da Cota: R$ {ParticipanteService.VALOR_COTA:.2f}")
    
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
    
    # Nome do participante
    nome = st.text_input("Nome do Participante")
    
    # Seleção de quantidade de cotas
    col1, col2 = st.columns(2)
    with col1:
        quantidade_cotas = st.number_input(
            "Quantidade de Cotas", 
            min_value=1, 
            value=1, 
            step=1,
            help="Cada cota dá direito a 6 números"
        )
    
    with col2:
        valor_total = ParticipanteService.calcular_valor_total(quantidade_cotas)
        st.write(f"Valor Total: R$ {valor_total:.2f}")
        
    # Status do pagamento
    status_pagamento = st.selectbox(
        "Status do Pagamento",
        options=["Pendente", "Pago", "Confirmado"],
        index=0
    )

    # Inicializar números selecionados se não existir
    if 'numeros_selecionados' not in st.session_state:
        st.session_state.numeros_selecionados = set()

    # Atualizar o contador para mostrar o total de números necessários
    numeros_necessarios = 6 * quantidade_cotas
    st.markdown(
        f"""
        <div class="contador-container">
            Selecione {numeros_necessarios - len(st.session_state.numeros_selecionados)} números
            ({len(st.session_state.numeros_selecionados)}/{numeros_necessarios} selecionados)
        </div>
        """,
        unsafe_allow_html=True
    )

    # Grid de números
    st.write("Selecione seus números:")
    
    # Criar grid de números usando columns
    for linha in range(6):
        cols = st.columns(10)
        for i in range(10):
            numero = linha * 10 + i + 1
            if numero <= 60:
                with cols[i]:
                    # Usar checkbox em vez de botão
                    is_selected = numero in st.session_state.numeros_selecionados
                    if st.checkbox(
                        str(numero),
                        value=is_selected,
                        key=f"num_{numero}",
                        disabled=len(st.session_state.numeros_selecionados) >= numeros_necessarios and not is_selected
                    ):
                        if numero not in st.session_state.numeros_selecionados:
                            st.session_state.numeros_selecionados.add(numero)
                    else:
                        if numero in st.session_state.numeros_selecionados:
                            st.session_state.numeros_selecionados.remove(numero)

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
        if st.form_submit_button("🎲 Limpar Seleção", type="secondary"):
            st.session_state.numeros_selecionados = set()
            st.rerun()
    
    with col2:
        submitted = st.form_submit_button("✅ Adicionar Participante", type="primary")
        if submitted:
            if not nome:
                st.error("Por favor, preencha o nome do participante!")
            elif len(st.session_state.numeros_selecionados) != numeros_necessarios:
                st.error(f"Por favor, escolha exatamente {numeros_necessarios} números!")
            else:
                novo_participante = Participante(
                    nome=nome,
                    valor_pago=valor_total,
                    numeros_escolhidos=list(st.session_state.numeros_selecionados),
                    status_pagamento=status_pagamento,
                    quantidade_cotas=quantidade_cotas
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
            'Qtd. Cotas': p.quantidade_cotas,
            'Valor_Pago': f"R$ {p.valor_pago:.2f}",
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