# app/db.py

import os
import oracledb
from dotenv import load_dotenv
from contextlib import contextmanager

# Carga las variables de entorno
load_dotenv()

# --- Configuración de Conexión ---
# Asegúrate de que estas variables estén definidas en tu archivo .env
USER = os.getenv("DB_USER", "GLOBALENGLISH")
PASSWORD = os.getenv("DB_PASS", "oracle")
DSN = os.getenv("DB_DSN", "localhost:1521/XEPDB1")

# print("Conexión:", USER, PASSWORD, DSN) # Se comenta para evitar logs innecesarios
# print("Conexión:", USER, PASSWORD, DSN)

_pool = None

def init_pool():
    """Inicializa el pool de conexiones si no existe."""
    global _pool
    if _pool is None:
        # Nota: La librería oracledb maneja la configuración del pool.
        _pool = oracledb.create_pool(user=USER, password=PASSWORD, dsn=DSN,
                                     min=1, max=5, increment=1)
    return _pool

def get_conn():
    """Adquiere una conexión del pool."""
    pool = init_pool()
    return pool.acquire()

def release_conn(conn):
    """Libera una conexión al pool."""
    pool = init_pool()
    # Verifica si la conexión existe y tiene un pool asociado antes de liberarla.
    if conn:
        pool.release(conn)

@contextmanager
def db_session():
    """
    Context manager para manejar la conexión, transacciones y liberación
    automáticamente usando el pool.
    
    Uso: with db_session() as conn: ...
    """
    conn = None
    try:
        # Adquirir conexión del pool
        conn = get_conn()
        yield conn
        # Si no hay excepción, hacer commit
        conn.commit()
    except Exception:
        # Si hay excepción, hacer rollback
        if conn:
            conn.rollback()
        # Vuelve a elevar la excepción para que el llamador la maneje
        raise
    finally:
        # Liberar la conexión al pool
        release_conn(conn)
