import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("DB_USER", "GLOBALENGLISH")
PASSWORD = os.getenv("DB_PASS", "oracle")
DSN = os.getenv("DB_DSN", "localhost:1521/XEPDB1")

print("Conexión:", USER, PASSWORD, DSN)

_pool = None

def init_pool():
    global _pool
    if _pool is None:
        _pool = oracledb.create_pool(user=USER, password=PASSWORD, dsn=DSN,
                                     min=1, max=5, increment=1)
    return _pool

def get_conn():
    pool = init_pool()
    return pool.acquire()

def release_conn(conn):
    pool = init_pool()
    pool.release(conn)
