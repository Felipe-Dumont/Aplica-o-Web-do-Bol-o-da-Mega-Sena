from dataclasses import dataclass
from datetime import datetime
from typing import List, Union

@dataclass
class Participante:
    nome: str
    valor_pago: float
    numeros_escolhidos: Union[List[int], str]
    quantidade_cotas: int = 1
    data_pagamento: str = None
    id: int = None
    status_pagamento: str = "Pendente"

    def __post_init__(self):
        if self.data_pagamento is None:
            self.data_pagamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Garantir que numeros_escolhidos seja uma lista de inteiros
        if isinstance(self.numeros_escolhidos, str):
            try:
                if ',' in self.numeros_escolhidos:
                    self.numeros_escolhidos = [int(n.strip()) for n in self.numeros_escolhidos.split(',') if n.strip()]
                else:
                    self.numeros_escolhidos = eval(self.numeros_escolhidos)
            except Exception as e:
                print(f"Erro ao converter números escolhidos: {e}")
                self.numeros_escolhidos = []