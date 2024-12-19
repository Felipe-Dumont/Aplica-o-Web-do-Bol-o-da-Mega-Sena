from typing import List
from models.participante import Participante
from config.database import get_db

class ParticipanteService:
    VALOR_COTA = 35.0  # Valor fixo da cota

    @staticmethod
    def adicionar_participante(participante: Participante) -> bool:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO participantes (
                        nome, valor_pago, numeros_escolhidos, 
                        status_pagamento, quantidade_cotas
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        participante.nome,
                        participante.valor_pago,
                        ','.join(map(str, participante.numeros_escolhidos)),
                        participante.status_pagamento,
                        participante.quantidade_cotas
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao adicionar participante: {e}")
            return False

    @staticmethod
    def calcular_valor_total(quantidade_cotas: int) -> float:
        return quantidade_cotas * ParticipanteService.VALOR_COTA

    @staticmethod
    def atualizar_status_pagamento(participante_id, novo_status):
        try:
            with get_db() as conn:
                cursor = conn.cursor()
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
    def listar_participantes() -> List[Participante]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM participantes")
            rows = cursor.fetchall()
            
            participantes = []
            for row in rows:
                # Converte a string de números de volta para lista
                numeros = [int(n) for n in row['numeros_escolhidos'].split(',') if n]
                
                participante = Participante(
                    id=row['id'],
                    nome=row['nome'],
                    valor_pago=row['valor_pago'],
                    numeros_escolhidos=numeros,
                    data_pagamento=row['data_pagamento'],
                    status_pagamento=row['status_pagamento'],
                    quantidade_cotas=row['quantidade_cotas']
                )
                participantes.append(participante)
            
            return participantes

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