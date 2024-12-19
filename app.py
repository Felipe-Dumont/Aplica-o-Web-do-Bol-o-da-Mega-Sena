import streamlit as st
import pandas as pd
from datetime import datetime
from config.database import init_db
from models.participante import Participante
from services.participante_service import ParticipanteService
from auth.auth_service import AuthService
from pages_.login import require_auth
import time

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

# Requer autentica��ão antes de continuar
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
    # Carregar página de participantes
    st.title("📋 Lista de Participantes")
    
    participantes = ParticipanteService.listar_participantes()
    if participantes:
        # Convertendo para DataFrame para exibição
        df_participantes = pd.DataFrame([
            {
                'ID': p.id,
                'Nome': p.nome,
                'Valor Pago': f"R$ {p.valor_pago:.2f}",
                'Números Escolhidos': ', '.join(f"{num:02d}" for num in sorted(p.numeros_escolhidos)),
                'Data Pagamento': p.data_pagamento,
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
        
        # Adicionar seção para atualizar status
        st.subheader("Atualizar Status de Pagamento")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            participante_id = st.selectbox(
                "Selecione o Participante",
                options=df_participantes['ID'].tolist(),
                format_func=lambda x: df_participantes[df_participantes['ID'] == x]['Nome'].iloc[0]
            )
        
        with col2:
            novo_status = st.selectbox(
                "Novo Status",
                options=["Pendente", "Pago", "Confirmado"],
                key="novo_status"
            )
        
        with col3:
            if st.button("Atualizar Status", type="primary"):
                if ParticipanteService.atualizar_status_pagamento(participante_id, novo_status):
                    st.success(f"Status atualizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao atualizar status")
        
        # Botão para baixar dados
        st.download_button(
            label="📥 Baixar dados em Excel",
            data=df_participantes.to_csv(index=False).encode('utf-8'),
            file_name='bolao_mega_sena.csv',
            mime='text/csv'
        )
    else:
        st.info("Nenhum participante cadastrado ainda.")

elif pagina == "🎯 Resultado":
    # Carregar página de resultado
    st.title("🎯 Resultado do Sorteio")
    
    # Input dos números sorteados
    numeros_sorteados = st.multiselect(
        "Selecione os 6 números sorteados:",
        options=list(range(1, 61)),
        format_func=lambda x: f"{x:02d}",
        max_selections=6
    )
    
    if len(numeros_sorteados) == 6:
        if st.button("🎲 Verificar Resultados", type="primary"):
            # Efeito de loading
            with st.spinner("Verificando resultados..."):
                time.sleep(2)  # Criar suspense
                
                # Buscar resultados
                resultados = ParticipanteService.verificar_resultados(numeros_sorteados)
                
                # Se houver ganhadores
                if resultados['ganhadores']:
                    st.balloons()  # Solta balões
                    
                    st.markdown("""
                        <div style='padding: 20px; background: linear-gradient(45deg, #FFD700, #FFA500); 
                                border-radius: 10px; text-align: center; animation: pulse 2s infinite;'>
                            <h2 style='color: #fff; text-shadow: 2px 2px 4px #000;'>
                                🎉 TEMOS GANHADORES! 🎉
                            </h2>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Lista de ganhadores
                    st.markdown("### 🏆 Ganhadores:")
                    for ganhador in resultados['ganhadores']:
                        st.markdown(f"""
                            <div style='background-color: #FFD700; padding: 15px; 
                                    border-radius: 8px; margin: 10px 0;'>
                                <h3 style='margin:0; color: #000;'>
                                    {ganhador['nome']} 
                                    <span style='float:right'>✨ {ganhador['acertos']} acertos ✨</span>
                                </h3>
                                <p style='margin:5px 0 0 0;'>Números: {', '.join(f"{n:02d}" for n in ganhador['numeros'])}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("😔 Não tivemos ganhadores com 6 acertos")
                    
                    # Mostrar maiores pontuadores
                    st.subheader("🎯 Maiores Pontuadores:")
                    for pontuador in resultados['maiores_pontuadores']:
                        cor = {
                            5: '#FFD700',  # Ouro
                            4: '#C0C0C0',  # Prata
                            3: '#CD7F32'   # Bronze
                        }.get(pontuador['acertos'], '#FFFFFF')
                        
                        st.markdown(f"""
                            <div style='background-color: {cor}; padding: 15px; 
                                    border-radius: 8px; margin: 10px 0; opacity: 0.9;'>
                                <h3 style='margin:0; color: #000;'>
                                    {pontuador['nome']} 
                                    <span style='float:right'>✨ {pontuador['acertos']} acertos ✨</span>
                                </h3>
                                <p style='margin:5px 0 0 0;'>
                                    Números: {', '.join(f"{n:02d}" for n in pontuador['numeros'])}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("Selecione os 6 números sorteados para verificar os resultados")