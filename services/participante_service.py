from typing import List
from models.participante import Participante
from config.database import get_db
import sqlite3

class ParticipanteService:
    VALOR_COTA = 35.0  # Valor fixo da cota

    @staticmethod
    def adicionar_participante(participante: Participante) -> bool:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Debug
                print(f"Tentando adicionar participante: {participante}")
                
                # Garantir que os números estejam em formato string
                numeros_str = ','.join(map(str, sorted(participante.numeros_escolhidos)))
                
                cursor.execute(
                    """
                    INSERT INTO participantes (
                        nome, 
                        valor_pago, 
                        numeros_escolhidos, 
                        status_pagamento, 
                        quantidade_cotas,
                        data_pagamento
                    )
                    VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
                    """,
                    (
                        participante.nome,
                        participante.valor_pago,
                        numeros_str,
                        participante.status_pagamento,
                        participante.quantidade_cotas
                    )
                )
                conn.commit()
                print("Participante adicionado com sucesso!")
                return True
        except Exception as e:
            print(f"Erro ao adicionar participante: {e}")
            return False

    @staticmethod
    def listar_participantes() -> List[Participante]:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        id,
                        nome,
                        valor_pago,
                        numeros_escolhidos,
                        datetime(data_pagamento, 'localtime') as data_pagamento,
                        status_pagamento,
                        quantidade_cotas
                    FROM participantes 
                    ORDER BY id DESC
                """)
                rows = cursor.fetchall()
                
                participantes = []
                for row in rows:
                    try:
                        # Converte a string de números de volta para lista
                        numeros_str = row[3] if row[3] else ''
                        numeros = [int(n.strip()) for n in numeros_str.split(',') if n.strip()]
                        
                        participante = Participante(
                            id=row[0],
                            nome=row[1],
                            valor_pago=float(row[2]),
                            numeros_escolhidos=numeros,
                            data_pagamento=row[4],
                            status_pagamento=row[5],
                            quantidade_cotas=int(row[6])
                        )
                        participantes.append(participante)
                        print(f"Participante carregado: {participante}")
                    except Exception as e:
                        print(f"Erro ao processar participante: {e}")
                        continue
                
                return participantes
        except Exception as e:
            print(f"Erro ao listar participantes: {e}")
            return []

    @staticmethod
    def calcular_valor_total(quantidade_cotas: int) -> float:
        return quantidade_cotas * ParticipanteService.VALOR_COTA

    @staticmethod
    def atualizar_status_pagamento(participante_id, novo_status):
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Atualizar status e data de pagamento se for marcado como pago
                if novo_status in ['Pago', 'Confirmado']:
                    cursor.execute("""
                        UPDATE participantes 
                        SET status_pagamento = ?,
                            data_pagamento = datetime('now', 'localtime')
                        WHERE id = ?
                    """, (novo_status, participante_id))
                else:
                    cursor.execute("""
                        UPDATE participantes 
                        SET status_pagamento = ?
                        WHERE id = ?
                    """, (novo_status, participante_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            return False

    @staticmethod
    def obter_estatisticas():
        participantes = ParticipanteService.listar_participantes()
        return {
            'total_participantes': len(participantes),
            'total_arrecadado': sum(p.valor_pago for p in participantes)
        }

    @staticmethod
    def analisar_numeros_repetidos():
        participantes = ParticipanteService.listar_participantes()
        todos_numeros = {}
        
        for participante in participantes:
            for num in participante.numeros_escolhidos:
                if num in todos_numeros:
                    todos_numeros[num].append(participante.nome)
                else:
                    todos_numeros[num] = [participante.nome]
        
        return {k:v for k,v in todos_numeros.items() if len(v) > 1} 