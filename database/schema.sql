CREATE TABLE IF NOT EXISTS participantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    valor_pago REAL NOT NULL,
    numeros_escolhidos TEXT NOT NULL,
    data_pagamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_pagamento TEXT DEFAULT 'Pendente',
    quantidade_cotas INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS auth_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    access_code_hash TEXT NOT NULL
); 