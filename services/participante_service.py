from typing import List
from models.participante import Participante
from config.database import get_db

class ParticipanteService:
    @staticmethod
    def adicionar_participante(participante: Participante) -> bool:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO participantes (nome, valor_pago, numeros_escolhidos, data_pagamento)
                VALUES (?, ?, ?, ?)
                """,
                (participante.nome, participante.valor_pago, str(sorted(participante.numeros_escolhidos)), participante.data_pagamento)
            )
            conn.commit()
            return True

    @staticmethod
    def listar_participantes() -> List[Participante]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM participantes")
            rows = cursor.fetchall()
            
            return [
                Participante(
                    id=row['id'],
                    nome=row['nome'],
                    valor_pago=row['valor_pago'],
                    numeros_escolhidos=row['numeros_escolhidos'],
                    data_pagamento=row['data_pagamento']
                )
                for row in rows
            ]

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