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
    .numeros-container {
        padding: 20px;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    .numeros-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
        gap: 8px;
        justify-items: center;
    }
    
    .numero-btn {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        border: 2px solid #4CAF50;
        background-color: white;
        color: #4CAF50;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
    }
    
    .numero-btn:hover {
        transform: scale(1.1);
        background-color: #e8f5e9;
    }
    
    .numero-btn.selecionado {
        background-color: #4CAF50;
        color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .numeros-selecionados {
        margin-top: 15px;
        padding: 10px;
        background: #e8f5e9;
        border-radius: 5px;
        text-align: center;
    }
    
    .numeros-selecionados span {
        display: inline-block;
        background: #4CAF50;
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        margin: 0 5px;
        line-height: 35px;
        font-weight: bold;
    }
    
    .contador-numeros {
        text-align: center;
        margin-bottom: 10px;
        font-weight: bold;
        color: #2E7D32;
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

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    valor_cota = st.number_input("Valor da Cota (R$)", min_value=1.0, value=10.0)

# Formulário para adicionar participante
with st.form("novo_participante", clear_on_submit=True):
    st.subheader("Adicionar Novo Participante")
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Participante")
    with col2:
        valor_pago = st.number_input("Valor Pago (R$)", min_value=0.0, value=valor_cota)
    
    st.markdown("### Escolha 6 números")
    
    # Criar grid de números usando colunas do Streamlit
    numeros_por_linha = 10
    total_numeros = 60
    
    # Inicializar números selecionados se não existir
    if 'numeros_selecionados' not in st.session_state:
        st.session_state.numeros_selecionados = set()
    
    # Criar grid de números
    for linha in range((total_numeros + numeros_por_linha - 1) // numeros_por_linha):
        cols = st.columns(numeros_por_linha)
        for i in range(numeros_por_linha):
            numero = linha * numeros_por_linha + i + 1
            if numero <= total_numeros:
                # Criar um checkbox estilizado como botão
                is_selected = numero in st.session_state.numeros_selecionados
                if cols[i].checkbox(
                    str(numero),
                    value=is_selected,
                    key=f"num_{numero}",
                    help="Clique para selecionar/desselecionar"
                ):
                    if numero not in st.session_state.numeros_selecionados and len(st.session_state.numeros_selecionados) < 6:
                        st.session_state.numeros_selecionados.add(numero)
                else:
                    if numero in st.session_state.numeros_selecionados:
                        st.session_state.numeros_selecionados.remove(numero)
    
    # Exibir números selecionados
    if st.session_state.numeros_selecionados:
        numeros_ordenados = sorted(st.session_state.numeros_selecionados)
        st.markdown(
            "<div style='text-align: center; margin: 20px 0; padding: 10px; "
            "background-color: #e8f5e9; border-radius: 5px;'>"
            "<b>Números selecionados:</b><br>" +
            " ".join([f"<span style='display: inline-block; width: 35px; height: 35px; "
                     f"line-height: 35px; border-radius: 50%; background-color: #4CAF50; "
                     f"color: white; margin: 5px; font-weight: bold;'>{num}</span>"
                     for num in numeros_ordenados]) +
            "</div>",
            unsafe_allow_html=True
        )
    
    # Botão de submit do formulário
    submitted = st.form_submit_button("Adicionar Participante")
    
    if submitted:
        if not nome:
            st.error("Por favor, preencha o nome do participante!")
        elif len(st.session_state.numeros_selecionados) != 6:
            st.error("Por favor, escolha exatamente 6 números!")
        else:
            novo_participante = Participante(
                nome=nome,
                valor_pago=valor_pago,
                numeros_escolhidos=list(st.session_state.numeros_selecionados)
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
            'Data_Pagamento': p.data_pagamento
        }
        for p in participantes
    ])
    
    st.dataframe(df_participantes, use_container_width=True)
    
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