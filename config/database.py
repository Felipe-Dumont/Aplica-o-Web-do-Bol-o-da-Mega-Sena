import sqlite3
from contextlib import contextmanager
import os

DATABASE_PATH = "database/bolao.db"

def init_db():
    os.makedirs("database", exist_ok=True)
    
    with get_db() as conn:
        with open('database/schema.sql', 'r') as f:
            conn.executescript(f.read())

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close() 