import streamlit as st
import pandas as pd
from services.participante_service import ParticipanteService
import time

def app():    
    # Input dos números sorteados
    st.subheader("Digite os números sorteados")
    
    # Usar multiselect para os números sorteados
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
                    # Efeito de celebração
                    st.balloons()  # Solta balões
                    
                    # Mensagem com efeito
                    st.markdown("""
                        <div style='padding: 20px; background: linear-gradient(45deg, #FFD700, #FFA500); 
                                border-radius: 10px; text-align: center; animation: pulse 2s infinite;'>
                            <h2 style='color: #fff; text-shadow: 2px 2px 4px #000;'>
                                🎉 TEMOS GANHADORES! 🎉
                            </h2>
                        </div>
                        <style>
                            @keyframes pulse {
                                0% { transform: scale(1); }
                                50% { transform: scale(1.05); }
                                100% { transform: scale(1); }
                            }
                        </style>
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
                
                # Se não houver ganhadores, mostrar maiores pontuadores
                else:
                    st.warning("😔 Não tivemos ganhadores com 6 acertos")
                    
                    # Mostrar maiores pontuadores
                    st.subheader("🎯 Maiores Pontuadores:")
                    for pontuador in resultados['maiores_pontuadores']:
                        # Cor baseada no número de acertos
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
                
                # Exibir números sorteados
                st.markdown("""
                    <div style='background-color: #4CAF50; padding: 15px; border-radius: 8px; 
                            margin: 20px 0; text-align: center;'>
                        <h3 style='color: white; margin: 0;'>Números Sorteados:</h3>
                        <div style='display: flex; justify-content: center; gap: 10px; margin-top: 10px;'>
                """, unsafe_allow_html=True)
                
                for num in sorted(numeros_sorteados):
                    st.markdown(f"""
                        <div style='background-color: white; color: #4CAF50; width: 40px; height: 40px; 
                                border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                font-weight: bold; font-size: 20px;'>
                            {num:02d}
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.info("Selecione os 6 números sorteados para verificar os resultados") 