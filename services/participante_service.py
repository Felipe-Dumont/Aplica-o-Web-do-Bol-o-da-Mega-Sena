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
                # Configurar para retornar dicionários
                conn.row_factory = sqlite3.Row
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
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
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
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM participantes ORDER BY id DESC")
                rows = cursor.fetchall()
                
                participantes = []
                for row in rows:
                    try:
                        # Converte a string de números de volta para lista
                        numeros = [int(n) for n in row['numeros_escolhidos'].split(',') if n]
                        
                        participante = Participante(
                            id=row['id'],
                            nome=row['nome'],
                            valor_pago=float(row['valor_pago']),
                            numeros_escolhidos=numeros,
                            data_pagamento=row['data_pagamento'],
                            status_pagamento=row['status_pagamento'],
                            quantidade_cotas=int(row['quantidade_cotas'])
                        )
                        participantes.append(participante)
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