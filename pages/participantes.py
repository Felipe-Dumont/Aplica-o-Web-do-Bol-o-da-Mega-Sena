import streamlit as st
import pandas as pd
from services.participante_service import ParticipanteService
from pages.login import require_auth

# Configuração da página
st.set_page_config(page_title="Listagem de Participantes", page_icon="📋")

# Requer autenticação antes de continuar
require_auth()

st.title("📋 Listagem de Participantes")

# Busca todos os participantes
participantes = ParticipanteService.listar_participantes()

if not participantes:
    st.info("Nenhum participante cadastrado ainda.")
else:
    # Adiciona filtros
    col1, col2 = st.columns(2)
    with col1:
        busca_nome = st.text_input("Buscar por nome")
    with col2:
        ordenar_por = st.selectbox(
            "Ordenar por",
            ["Nome", "Data de Pagamento", "Valor Pago"]
        )

    # Prepara os dados para exibição
    dados_participantes = []
    for p in participantes:
        if busca_nome.lower() in p.nome.lower() or not busca_nome:
            dados_participantes.append({
                'Nome': p.nome,
                'Valor Pago': f"R$ {p.valor_pago:.2f}",
                'Números Escolhidos': str(sorted(p.numeros_escolhidos)),
                'Data de Pagamento': p.data_pagamento
            })

    # Converte para DataFrame
    df = pd.DataFrame(dados_participantes)
    
    # Ordena os dados
    if ordenar_por == "Nome":
        df = df.sort_values("Nome")
    elif ordenar_por == "Data de Pagamento":
        df = df.sort_values("Data de Pagamento", ascending=False)
    elif ordenar_por == "Valor Pago":
        df["Valor Ordenação"] = df["Valor Pago"].str.replace("R$ ", "").astype(float)
        df = df.sort_values("Valor Ordenação", ascending=False)
        df = df.drop("Valor Ordenação", axis=1)

    # Exibe as estatísticas em cards
    estatisticas = ParticipanteService.obter_estatisticas()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Participantes", estatisticas['total_participantes'])
    with col2:
        st.metric("Total Arrecadado", f"R$ {estatisticas['total_arrecadado']:.2f}")
    with col3:
        media = estatisticas['total_arrecadado'] / estatisticas['total_participantes'] if estatisticas['total_participantes'] > 0 else 0
        st.metric("Média por Participante", f"R$ {media:.2f}")

    # Exibe a tabela com os dados
    st.subheader("Lista Detalhada")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Adiciona opção de download
    st.download_button(
        label="📥 Baixar como Excel",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='participantes_bolao.csv',
        mime='text/csv',
    )

    # Exibe análise de números repetidos
    st.subheader("Análise de Números Repetidos")
    numeros_repetidos = ParticipanteService.analisar_numeros_repetidos()
    
    if not numeros_repetidos:
        st.success("Não há números repetidos entre os participantes!")
    else:
        for numero, pessoas in numeros_repetidos.items():
            with st.expander(f"Número {numero} - {len(pessoas)} pessoas"):
                st.write(", ".join(pessoas)) 