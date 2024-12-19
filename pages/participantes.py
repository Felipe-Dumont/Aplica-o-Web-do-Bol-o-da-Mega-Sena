import streamlit as st
import pandas as pd
from services.participante_service import ParticipanteService

def app():
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