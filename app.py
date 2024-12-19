import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração inicial da página
st.set_page_config(page_title="Bolão Mega da Virada", page_icon="🎲")

# Inicialização do estado da sessão
if 'participantes' not in st.session_state:
    st.session_state.participantes = pd.DataFrame(columns=['Nome', 'Valor_Pago', 'Numeros_Escolhidos', 'Data_Pagamento'])

# Título principal
st.title("🎲 Bolão Mega da Virada 2024")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    valor_cota = st.number_input("Valor da Cota (R$)", min_value=1.0, value=10.0)

# Formulário para adicionar participante
with st.form("novo_participante"):
    st.subheader("Adicionar Novo Participante")
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Participante")
    with col2:
        valor_pago = st.number_input("Valor Pago (R$)", min_value=0.0, value=valor_cota)
    
    numeros = st.multiselect("Escolha 6 números", options=range(1, 61), max_selections=6)
    
    submitted = st.form_submit_button("Adicionar Participante")
    
    if submitted:
        if len(numeros) != 6:
            st.error("Por favor, escolha exatamente 6 números!")
        else:
            novo_participante = {
                'Nome': nome,
                'Valor_Pago': valor_pago,
                'Numeros_Escolhidos': str(sorted(numeros)),
                'Data_Pagamento': datetime.now().strftime('%d/%m/%Y')
            }
            st.session_state.participantes = pd.concat([
                st.session_state.participantes,
                pd.DataFrame([novo_participante])
            ], ignore_index=True)
            st.success("Participante adicionado com sucesso!")

# Exibição dos participantes
if not st.session_state.participantes.empty:
    st.subheader("Lista de Participantes")
    st.dataframe(st.session_state.participantes, use_container_width=True)
    
    # Análise dos números
    st.subheader("Análise dos Números")
    
    # Contagem de números repetidos
    todos_numeros = {}
    for idx, row in st.session_state.participantes.iterrows():
        numeros = eval(row['Numeros_Escolhidos'])
        for num in numeros:
            if num in todos_numeros:
                todos_numeros[num].append(row['Nome'])
            else:
                todos_numeros[num] = [row['Nome']]
    
    numeros_repetidos = {k:v for k,v in todos_numeros.items() if len(v) > 1}
    
    if numeros_repetidos:
        st.warning("Números escolhidos por mais de uma pessoa:")
        for num, pessoas in numeros_repetidos.items():
            st.write(f"Número {num}: {', '.join(pessoas)}")
    
    # Estatísticas
    total_arrecadado = st.session_state.participantes['Valor_Pago'].sum()
    st.subheader("Estatísticas")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Participantes", len(st.session_state.participantes))
    with col2:
        st.metric("Total Arrecadado", f"R$ {total_arrecadado:.2f}")

# Botão para baixar dados
if not st.session_state.participantes.empty:
    st.download_button(
        label="Baixar dados em Excel",
        data=st.session_state.participantes.to_csv(index=False).encode('utf-8'),
        file_name='bolao_mega_sena.csv',
        mime='text/csv'
    )