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

# Inicialização do estado para números selecionados
if 'numeros_selecionados' not in st.session_state:
    st.session_state.numeros_selecionados = set()

# Função para alternar seleção de número
def toggle_numero(numero):
    if numero in st.session_state.numeros_selecionados:
        st.session_state.numeros_selecionados.remove(numero)
    elif len(st.session_state.numeros_selecionados) < 6:
        st.session_state.numeros_selecionados.add(numero)

# Formulário para adicionar participante
with st.form("novo_participante"):
    st.subheader("Adicionar Novo Participante")
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Participante")
    with col2:
        valor_pago = st.number_input("Valor Pago (R$)", min_value=0.0, value=valor_cota)
    
    st.markdown("### Escolha 6 números")
    
    # Container para os números
    html_numeros = '''
    <div class="numeros-container">
        <div class="contador-numeros">
            Selecionados: <span id="contador">0</span>/6
        </div>
        <div class="numeros-grid">
    '''
    
    for numero in range(1, 61):
        classe = "numero-btn selecionado" if numero in st.session_state.numeros_selecionados else "numero-btn"
        html_numeros += f'''
            <button type="button" 
                class="{classe}"
                onclick="handleNumeroClick({numero})"
                id="num-{numero}">
                {numero}
            </button>
        '''
    
    html_numeros += '''
        </div>
        <div class="numeros-selecionados" id="numeros-display">
            Números selecionados: 
        </div>
    </div>
    '''

    # JavaScript atualizado para melhor interação
    js_code = '''
    <script>
        function atualizarContador() {
            const selecionados = document.getElementsByClassName('selecionado').length;
            document.getElementById('contador').textContent = selecionados;
        }
        
        function atualizarNumerosDisplay() {
            const selecionados = Array.from(document.getElementsByClassName('selecionado'))
                .map(btn => parseInt(btn.textContent))
                .sort((a, b) => a - b);
            
            const display = document.getElementById('numeros-display');
            display.innerHTML = 'Números selecionados: ' + 
                selecionados.map(num => `<span>${num}</span>`).join(' ');
        }
        
        function handleNumeroClick(numero) {
            const btn = document.getElementById('num-' + numero);
            const isSelected = btn.classList.contains('selecionado');
            const selectedCount = document.getElementsByClassName('selecionado').length;
            
            if (!isSelected && selectedCount < 6) {
                btn.classList.add('selecionado');
            } else if (isSelected) {
                btn.classList.remove('selecionado');
            }
            
            atualizarContador();
            atualizarNumerosDisplay();
            
            // Envia o evento para o Streamlit
            const data = {numero: numero};
            window.parent.postMessage({type: "numero_clicked", data: data}, "*");
        }
        
        // Inicialização
        atualizarContador();
        atualizarNumerosDisplay();
    </script>
    '''

    st.components.v1.html(html_numeros + js_code, height=500)
    
    submitted = st.form_submit_button("Adicionar Participante")
    
    if submitted:
        if len(st.session_state.numeros_selecionados) != 6:
            st.error("Por favor, escolha exatamente 6 números!")
        else:
            novo_participante = Participante(
                nome=nome,
                valor_pago=valor_pago,
                numeros_escolhidos=list(st.session_state.numeros_selecionados)
            )
            
            if ParticipanteService.adicionar_participante(novo_participante):
                st.success("Participante adicionado com sucesso!")
                # Limpa os números selecionados após sucesso
                st.session_state.numeros_selecionados = set()
                st.rerun()

# Componente JavaScript para capturar eventos de clique
components_js = """
<script>
    window.addEventListener('message', function(e) {
        if (e.data.type === 'numero_clicked') {
            window.parent.postMessage({
                type: 'streamlit:set_widget_value',
                data: {
                    widgetId: 'numero_clicked',
                    value: e.data.data.numero
                }
            }, '*');
        }
    });
</script>
"""
st.components.v1.html(components_js, height=0)

# Captura eventos de clique nos números
numero_clicked = st.empty()
if numero_clicked:
    toggle_numero(numero_clicked)

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