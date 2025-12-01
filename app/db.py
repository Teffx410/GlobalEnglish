# app/db.py

import os
import oracledb
from dotenv import load_dotenv
from contextlib import contextmanager

# ================================
#  CARGA DE VARIABLES DE ENTORNO
# ================================
load_dotenv()

DB_USER = os.getenv("DB_USER", "GLOBALENGLISH")
DB_PASS = os.getenv("DB_PASS", "oracle")
DB_DSN  = os.getenv("DB_DSN", "localhost:1521/XEPDB1")

# ================================
#  POOL DE CONEXIONES GLOBAL
# ================================
_pool = None


def init_pool():
    """
    Inicializa el pool de conexiones (solo una vez).
    """
    global _pool

    if _pool is None:
        _pool = oracledb.create_pool(
            user=DB_USER,
            password=DB_PASS,
            dsn=DB_DSN,
            min=1,
            max=5,
            increment=1,
            homogeneous=True
        )

    return _pool


def get_conn():
    """
    Obtiene una conexión activa desde el pool.
    """
    pool = init_pool()
    conn = pool.acquire()
    return conn


def release_conn(conn):
    """
    Libera una conexión activa al pool.
    """
    if conn:
        try:
            pool = init_pool()
            pool.release(conn)
        except Exception:
            pass  # Evita errores silenciosamente si ya fue liberada


# ================================
#  CONTEXT MANAGER DE SESIÓN
# ================================
@contextmanager
def db_session():
    """
    Maneja automáticamente:
    - adquisición de conexión,
    - commit o rollback,
    - liberación al pool.

    Uso:
        with db_session() as conn:
            cur = conn.cursor()
            cur.execute(...)
    """
    conn = None
    try:
        conn = get_conn()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        release_conn(conn)
