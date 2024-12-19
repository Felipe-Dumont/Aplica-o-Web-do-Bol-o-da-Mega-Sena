from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Participante:
    nome: str
    valor_pago: float
    numeros_escolhidos: List[int]
    data_pagamento: str = None
    id: int = None
    status_pagamento: str = "Pendente"

    def __post_init__(self):
        if self.data_pagamento is None:
            self.data_pagamento = datetime.now().strftime('%d/%m/%Y')
        
        if isinstance(self.numeros_escolhidos, str):
            self.numeros_escolhidos = eval(self.numeros_escolhidos) 