CREATE TABLE IF NOT EXISTS participantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    valor_pago REAL NOT NULL,
    numeros_escolhidos TEXT NOT NULL,
    data_pagamento TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    access_code_hash TEXT NOT NULL
); 